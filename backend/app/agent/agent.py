"""
OpenDomain AI Agent.

Uses Claude via Bedrock with tool-use to execute platform actions
on behalf of the user through natural language.
"""

import json
import logging
import uuid

from anthropic import AnthropicBedrock
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.agent.tools import TOOLS
from backend.app.core.config import settings
from backend.app.models.domain import Domain
from backend.app.models.user import User
from backend.app.schemas.domain import DomainRegister, DomainSearch, DomainTransferIn, DomainUpdate
from backend.app.schemas.dns import DnsRecordCreate, DnsRecordUpdate
from backend.app.services.dns_service import DnsService
from backend.app.services.domain_service import DomainService
from backend.app.services.whois_service import WhoisService

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the OpenDomain assistant, an AI agent for an open-source domain registrar platform.

You help users with all domain management tasks:
- Searching for and registering domains
- Managing DNS records (A, AAAA, CNAME, MX, TXT, NS, SRV, CAA)
- Transferring domains in from other registrars
- Configuring WHOIS privacy, auto-renewal, and transfer locks
- Applying DNS templates for popular services (GitHub Pages, Google Workspace, Vercel, etc.)
- Looking up WHOIS information
- Managing contacts for domain registration
- Exporting DNS zone files

Be concise and action-oriented. When the user describes what they want, use the appropriate tool to do it.
If you need more information (like which domain or a missing parameter), ask.
When showing results, format them clearly. For DNS records, use a table-like format.
Always confirm destructive actions (deleting domains/records, disabling privacy) before executing."""

_conversations: dict[str, list[dict]] = {}


class OpenDomainAgent:
    def __init__(self, db: AsyncSession, user: User):
        self.db = db
        self.user = user
        self.domain_service = DomainService(db)
        self.dns_service = DnsService(db)
        self.whois_service = WhoisService()
        self.client = AnthropicBedrock(
            aws_region=settings.aws_region,
            aws_access_key=settings.aws_access_key_id,
            aws_secret_key=settings.aws_secret_access_key,
        )

    async def process_message(self, message: str, conversation_id: str | None = None) -> dict:
        conv_id = conversation_id or str(uuid.uuid4())
        if conv_id not in _conversations:
            _conversations[conv_id] = []

        _conversations[conv_id].append({"role": "user", "content": message})

        actions_taken = []
        messages = list(_conversations[conv_id])

        while True:
            response = self.client.messages.create(
                model=settings.anthropic_model,
                max_tokens=8192,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=messages,
            )

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = await self._execute_tool(block.name, block.input)
                        actions_taken.append({
                            "tool": block.name,
                            "input": block.input,
                            "success": "error" not in result,
                        })
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result),
                        })

                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})
            else:
                text = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        text += block.text
                _conversations[conv_id] = messages
                _conversations[conv_id].append({"role": "assistant", "content": text})

                return {
                    "response": text,
                    "conversation_id": conv_id,
                    "actions_taken": actions_taken if actions_taken else None,
                }

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> dict:
        try:
            match tool_name:
                case "search_domains":
                    results = await self.domain_service.search(
                        tool_input["query"], tool_input.get("tlds")
                    )
                    return {"results": [r.model_dump() for r in results]}

                case "register_domain":
                    data = DomainRegister(
                        domain=tool_input["domain"],
                        period_years=tool_input.get("period_years", 1),
                        registrant_contact_id=uuid.UUID(tool_input["contact_id"]),
                        privacy_enabled=tool_input.get("privacy_enabled", True),
                        auto_renew=tool_input.get("auto_renew", True),
                    )
                    domain = await self.domain_service.register(data, self.user)
                    return {"domain": _domain_to_dict(domain)}

                case "list_domains":
                    domains = await self.domain_service.list_for_user(
                        self.user.id, tool_input.get("status"), 1, 100
                    )
                    return {"domains": [_domain_to_dict(d) for d in domains]}

                case "get_domain_details":
                    domain = await self._find_domain_by_name(tool_input["domain_name"])
                    if not domain:
                        return {"error": f"Domain '{tool_input['domain_name']}' not found in your account"}
                    return {"domain": _domain_to_dict(domain)}

                case "update_domain":
                    domain = await self._find_domain_by_name(tool_input["domain_name"])
                    if not domain:
                        return {"error": f"Domain '{tool_input['domain_name']}' not found"}
                    updates = {k: v for k, v in tool_input.items() if k != "domain_name" and v is not None}
                    data = DomainUpdate(**updates)
                    updated = await self.domain_service.update(domain.id, data, self.user.id)
                    return {"domain": _domain_to_dict(updated)}

                case "renew_domain":
                    domain = await self._find_domain_by_name(tool_input["domain_name"])
                    if not domain:
                        return {"error": f"Domain '{tool_input['domain_name']}' not found"}
                    renewed = await self.domain_service.renew(
                        domain.id, tool_input.get("years", 1), self.user.id
                    )
                    return {"domain": _domain_to_dict(renewed)}

                case "manage_dns_records":
                    return await self._handle_dns(tool_input)

                case "apply_dns_template":
                    domain = await self._find_domain_by_name(tool_input["domain_name"])
                    if not domain:
                        return {"error": f"Domain '{tool_input['domain_name']}' not found"}
                    zone = await self.dns_service.apply_template(
                        domain.id, tool_input["template"], tool_input.get("params", {}), self.user.id
                    )
                    return {"zone": zone.zone_name, "template": tool_input["template"], "records_added": len(zone.records)}

                case "whois_lookup":
                    result = await self.whois_service.lookup(tool_input["domain_name"])
                    return {
                        "domain": result.domain_name,
                        "registrar": result.registrar,
                        "creation_date": str(result.creation_date) if result.creation_date else None,
                        "expiration_date": str(result.expiration_date) if result.expiration_date else None,
                        "nameservers": result.nameservers,
                        "status": result.status,
                    }

                case "transfer_domain_in":
                    data = DomainTransferIn(
                        domain=tool_input["domain_name"],
                        auth_code=tool_input["auth_code"],
                        registrant_contact_id=uuid.UUID(tool_input["contact_id"]),
                    )
                    transfer = await self.domain_service.initiate_transfer_in(data, self.user)
                    return {"transfer_id": str(transfer.id), "status": transfer.status}

                case "manage_contacts":
                    return await self._handle_contacts(tool_input)

                case "export_dns_zone":
                    domain = await self._find_domain_by_name(tool_input["domain_name"])
                    if not domain:
                        return {"error": f"Domain '{tool_input['domain_name']}' not found"}
                    export = await self.dns_service.export_zone_file(domain.id, self.user.id)
                    return {"zone_name": export.zone_name, "zone_file": export.zone_file}

                case _:
                    return {"error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            logger.exception("Tool execution error: %s", tool_name)
            return {"error": str(e)}

    async def _find_domain_by_name(self, name: str) -> Domain | None:
        result = await self.db.execute(
            select(Domain).where(Domain.name == name.lower(), Domain.owner_id == self.user.id)
        )
        return result.scalar_one_or_none()

    async def _handle_dns(self, tool_input: dict) -> dict:
        domain = await self._find_domain_by_name(tool_input["domain_name"])
        if not domain:
            return {"error": f"Domain '{tool_input['domain_name']}' not found"}

        action = tool_input["action"]
        if action == "list":
            zone = await self.dns_service.get_zone(domain.id, self.user.id)
            if not zone:
                return {"records": []}
            return {"records": [
                {
                    "id": str(r.id), "type": r.record_type, "name": r.name,
                    "content": r.content, "ttl": r.ttl, "priority": r.priority,
                }
                for r in zone.records
            ]}
        elif action == "create":
            data = DnsRecordCreate(
                record_type=tool_input["record_type"],
                name=tool_input["name"],
                content=tool_input["content"],
                ttl=tool_input.get("ttl", 3600),
                priority=tool_input.get("priority"),
            )
            record = await self.dns_service.create_record(domain.id, data, self.user.id)
            return {"record": {"id": str(record.id), "type": record.record_type, "name": record.name, "content": record.content}}
        elif action == "update":
            data = DnsRecordUpdate(
                content=tool_input.get("content"),
                ttl=tool_input.get("ttl"),
                priority=tool_input.get("priority"),
            )
            record = await self.dns_service.update_record(
                domain.id, uuid.UUID(tool_input["record_id"]), data, self.user.id
            )
            return {"record": {"id": str(record.id), "type": record.record_type, "name": record.name, "content": record.content}}
        elif action == "delete":
            await self.dns_service.delete_record(domain.id, uuid.UUID(tool_input["record_id"]), self.user.id)
            return {"deleted": True}

        return {"error": f"Unknown DNS action: {action}"}

    async def _handle_contacts(self, tool_input: dict) -> dict:
        from backend.app.models.contact import Contact
        action = tool_input["action"]

        if action == "list":
            result = await self.db.execute(select(Contact).where(Contact.user_id == self.user.id))
            contacts = result.scalars().all()
            return {"contacts": [
                {"id": str(c.id), "label": c.label, "name": f"{c.first_name} {c.last_name}", "email": c.email}
                for c in contacts
            ]}
        elif action == "create":
            contact = Contact(
                user_id=self.user.id,
                label=tool_input.get("label", "Default"),
                first_name=tool_input["first_name"],
                last_name=tool_input["last_name"],
                organization=tool_input.get("organization"),
                email=tool_input["email"],
                phone=tool_input["phone"],
                address_line1=tool_input["address_line1"],
                city=tool_input["city"],
                state_province=tool_input.get("state_province"),
                postal_code=tool_input["postal_code"],
                country_code=tool_input["country_code"],
            )
            self.db.add(contact)
            await self.db.flush()
            await self.db.refresh(contact)
            return {"contact": {"id": str(contact.id), "label": contact.label, "name": f"{contact.first_name} {contact.last_name}"}}
        elif action == "delete":
            result = await self.db.execute(
                select(Contact).where(Contact.id == uuid.UUID(tool_input["contact_id"]), Contact.user_id == self.user.id)
            )
            contact = result.scalar_one_or_none()
            if not contact:
                return {"error": "Contact not found"}
            await self.db.delete(contact)
            return {"deleted": True}

        return {"error": f"Unknown contact action: {action}"}


def _domain_to_dict(domain: Domain) -> dict:
    return {
        "id": str(domain.id),
        "name": domain.name,
        "tld": domain.tld,
        "status": domain.status,
        "auto_renew": domain.auto_renew,
        "privacy_enabled": domain.privacy_enabled,
        "locked": domain.locked,
        "nameservers": domain.nameservers,
        "registration_date": str(domain.registration_date),
        "expiry_date": str(domain.expiry_date),
        "price_cents": domain.price_cents,
        "renewal_price_cents": domain.renewal_price_cents,
    }
