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

You help users with ALL platform tasks:
- Searching for and registering domains (single or bulk)
- Managing DNS records and applying templates (GitHub Pages, Vercel, Google Workspace, etc.)
- DNSSEC management (enable, disable, key rotation)
- Domain transfers in/out
- WHOIS lookups and privacy management
- Contact management for domain registration
- Monitoring: domain expiry alerts, uptime checks, domain availability watches, SSL tracking
- Webhooks: event-driven HTTP callbacks for domain events
- Marketplace: listing domains for sale, browsing, making offers
- Email forwarding: set up forwarding rules for any domain
- SSL/TLS certificates: request, renew, revoke via Let's Encrypt
- Billing: view invoices, transactions, payment methods
- API keys: create and manage programmatic access tokens
- Bulk operations: register, renew, lock/unlock multiple domains at once
- DNS zone export/import in BIND format

Be concise and action-oriented. When the user describes what they want, use the appropriate tool.
If you need more information, ask. Format results clearly.
Always confirm destructive actions before executing."""

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

                case "manage_monitoring":
                    return await self._handle_monitoring(tool_input)

                case "manage_webhooks":
                    return await self._handle_webhooks(tool_input)

                case "manage_marketplace":
                    return await self._handle_marketplace(tool_input)

                case "manage_email_forwards":
                    return await self._handle_email_forwards(tool_input)

                case "manage_ssl":
                    return await self._handle_ssl(tool_input)

                case "manage_billing":
                    return await self._handle_billing(tool_input)

                case "manage_api_keys":
                    return await self._handle_api_keys(tool_input)

                case "bulk_operations":
                    return await self._handle_bulk(tool_input)

                case "manage_dnssec":
                    return await self._handle_dnssec(tool_input)

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


    async def _handle_monitoring(self, tool_input: dict) -> dict:
        from backend.app.services.monitoring_service import MonitoringService
        svc = MonitoringService(self.db)
        action = tool_input["action"]
        if action == "create_watch":
            watch = await svc.create_domain_watch(self.user.id, tool_input.get("domain_name", ""))
            return {"watch_id": str(watch.id), "domain": watch.domain_name}
        elif action == "list_watches":
            watches = await svc.list_domain_watches(self.user.id)
            return {"watches": [{"id": str(w.id), "domain": w.domain_name, "available": w.is_available} for w in watches]}
        elif action == "create_uptime":
            check = await svc.create_uptime_check(self.user.id, tool_input)
            return {"check_id": str(check.id), "url": check.url}
        elif action == "list_uptime":
            checks = await svc.list_uptime_checks(self.user.id)
            return {"checks": [{"id": str(c.id), "url": c.url, "status": c.status} for c in checks]}
        elif action == "list_alerts":
            alerts = await svc.list_alerts(self.user.id)
            return {"alerts": [{"id": str(a.id), "type": a.alert_type, "title": a.title, "status": a.status} for a in alerts]}
        elif action == "acknowledge_alert":
            await svc.acknowledge_alert(uuid.UUID(tool_input["alert_id"]), self.user.id)
            return {"acknowledged": True}
        return {"error": f"Unknown monitoring action: {action}"}

    async def _handle_webhooks(self, tool_input: dict) -> dict:
        from backend.app.services.webhook_service import WebhookService
        svc = WebhookService(self.db)
        action = tool_input["action"]
        if action == "create":
            wh = await svc.create_webhook(self.user.id, tool_input)
            return {"webhook_id": str(wh.id), "url": wh.url}
        elif action == "list":
            webhooks = await svc.list_webhooks(self.user.id)
            return {"webhooks": [{"id": str(w.id), "url": w.url, "events": w.events} for w in webhooks]}
        elif action == "delete":
            await svc.delete_webhook(uuid.UUID(tool_input["webhook_id"]), self.user.id)
            return {"deleted": True}
        return {"error": f"Unknown webhook action: {action}"}

    async def _handle_marketplace(self, tool_input: dict) -> dict:
        from backend.app.services.marketplace_service import MarketplaceService
        svc = MarketplaceService(self.db)
        action = tool_input["action"]
        if action == "browse":
            listings = await svc.list_listings()
            return {"listings": [{"id": str(l.id), "price_cents": l.asking_price_cents, "status": l.status} for l in listings]}
        elif action == "create_listing":
            domain = await self._find_domain_by_name(tool_input["domain_name"])
            if not domain:
                return {"error": f"Domain '{tool_input['domain_name']}' not found"}
            listing = await svc.create_listing(self.user.id, {"domain_id": str(domain.id), "asking_price_cents": tool_input["price_cents"]})
            return {"listing_id": str(listing.id)}
        elif action == "make_offer":
            offer = await svc.create_offer(self.user.id, {"listing_id": tool_input["listing_id"], "amount_cents": tool_input["offer_amount_cents"], "message": tool_input.get("message")})
            return {"offer_id": str(offer.id)}
        elif action == "my_offers":
            offers = await svc.list_my_offers(self.user.id)
            return {"offers": [{"id": str(o.id), "amount_cents": o.amount_cents, "status": o.status} for o in offers]}
        return {"error": f"Unknown marketplace action: {action}"}

    async def _handle_email_forwards(self, tool_input: dict) -> dict:
        from backend.app.services.email_forward_service import EmailForwardService
        svc = EmailForwardService(self.db)
        domain = await self._find_domain_by_name(tool_input["domain_name"])
        if not domain:
            return {"error": f"Domain '{tool_input['domain_name']}' not found"}
        action = tool_input["action"]
        if action == "create":
            fwd = await svc.create_forward(self.user.id, {"domain_id": str(domain.id), "source_address": tool_input["source_address"], "destination_email": tool_input["destination_email"]})
            return {"forward_id": str(fwd.id), "source": fwd.source_address, "destination": fwd.destination_email}
        elif action == "list":
            forwards = await svc.list_forwards(domain.id, self.user.id)
            return {"forwards": [{"id": str(f.id), "source": f.source_address, "destination": f.destination_email, "active": f.active} for f in forwards]}
        elif action == "delete":
            await svc.delete_forward(uuid.UUID(tool_input["forward_id"]), self.user.id)
            return {"deleted": True}
        return {"error": f"Unknown email forward action: {action}"}

    async def _handle_ssl(self, tool_input: dict) -> dict:
        from backend.app.services.ssl_service import SslService
        svc = SslService(self.db)
        action = tool_input["action"]
        if action == "request":
            domain = await self._find_domain_by_name(tool_input["domain_name"])
            if not domain:
                return {"error": f"Domain '{tool_input['domain_name']}' not found"}
            cert = await svc.request_certificate(self.user.id, {"domain_id": str(domain.id)})
            return {"cert_id": str(cert.id), "status": cert.status}
        elif action == "list":
            certs = await svc.list_certificates(self.user.id)
            return {"certificates": [{"id": str(c.id), "status": c.status, "domain_names": c.domain_names} for c in certs]}
        elif action == "revoke":
            await svc.revoke_certificate(uuid.UUID(tool_input["cert_id"]), self.user.id)
            return {"revoked": True}
        elif action == "renew":
            cert = await svc.renew_certificate(uuid.UUID(tool_input["cert_id"]), self.user.id)
            return {"cert_id": str(cert.id), "status": cert.status}
        return {"error": f"Unknown SSL action: {action}"}

    async def _handle_billing(self, tool_input: dict) -> dict:
        from backend.app.services.billing_service import BillingService
        svc = BillingService(self.db)
        action = tool_input["action"]
        if action == "list_invoices":
            invoices = await svc.list_invoices(self.user.id)
            return {"invoices": [{"id": str(i.id), "number": i.invoice_number, "status": i.status, "total_cents": i.total_cents} for i in invoices]}
        elif action == "list_transactions":
            txs = await svc.list_transactions(self.user.id)
            return {"transactions": [{"id": str(t.id), "type": t.transaction_type, "amount_cents": t.amount_cents, "description": t.description} for t in txs]}
        elif action == "list_payment_methods":
            methods = await svc.list_payment_methods(self.user.id)
            return {"payment_methods": [{"id": str(m.id), "type": m.method_type, "label": m.label, "default": m.is_default} for m in methods]}
        return {"error": f"Unknown billing action: {action}"}

    async def _handle_api_keys(self, tool_input: dict) -> dict:
        from backend.app.services.api_key_service import ApiKeyService
        svc = ApiKeyService(self.db)
        action = tool_input["action"]
        if action == "create":
            key, raw = await svc.create_key(self.user.id, {"name": tool_input["name"], "scopes": tool_input.get("scopes")})
            return {"key_id": str(key.id), "name": key.name, "key": raw, "prefix": key.prefix}
        elif action == "list":
            keys = await svc.list_keys(self.user.id)
            return {"keys": [{"id": str(k.id), "name": k.name, "prefix": k.prefix, "active": k.active} for k in keys]}
        elif action == "revoke":
            await svc.revoke_key(uuid.UUID(tool_input["key_id"]), self.user.id)
            return {"revoked": True}
        return {"error": f"Unknown API key action: {action}"}

    async def _handle_bulk(self, tool_input: dict) -> dict:
        from backend.app.services.bulk_service import BulkService
        svc = BulkService(self.db)
        action = tool_input["action"]
        if action == "register":
            result = await svc.bulk_register(self.user, tool_input.get("domains", []))
            return result
        elif action == "renew":
            domains = tool_input.get("domain_names", [])
            domain_ids = []
            for name in domains:
                d = await self._find_domain_by_name(name)
                if d:
                    domain_ids.append(str(d.id))
            result = await svc.bulk_renew(self.user.id, {"domain_ids": domain_ids, "years": tool_input.get("years", 1)})
            return result
        elif action in ("lock", "unlock"):
            domains = tool_input.get("domain_names", [])
            domain_ids = []
            for name in domains:
                d = await self._find_domain_by_name(name)
                if d:
                    domain_ids.append(str(d.id))
            result = await svc.bulk_lock(self.user.id, domain_ids, lock=(action == "lock"))
            return result
        return {"error": f"Unknown bulk action: {action}"}

    async def _handle_dnssec(self, tool_input: dict) -> dict:
        from backend.app.services.dnssec_service import DnssecService
        svc = DnssecService(self.db)
        domain = await self._find_domain_by_name(tool_input["domain_name"])
        if not domain:
            return {"error": f"Domain '{tool_input['domain_name']}' not found"}
        action = tool_input["action"]
        if action == "enable":
            await svc.enable_dnssec(domain.id, self.user.id, tool_input.get("algorithm", "ECDSAP256SHA256"))
            return {"enabled": True, "domain": domain.name}
        elif action == "disable":
            await svc.disable_dnssec(domain.id, self.user.id)
            return {"disabled": True, "domain": domain.name}
        elif action == "get_ds":
            ds = await svc.get_ds_record(domain.id, self.user.id)
            return {"ds_record": ds}
        elif action == "rotate_keys":
            await svc.rotate_keys(domain.id, self.user.id)
            return {"rotated": True, "domain": domain.name}
        return {"error": f"Unknown DNSSEC action: {action}"}


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
