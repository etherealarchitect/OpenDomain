"""
Async EPP (Extensible Provisioning Protocol) client.

Implements RFC 5730-5734 for domain registration, transfer, and management.
When settings.epp_simulate is True, all operations return simulated success responses
so the platform can run locally without a live registry connection.
"""

import asyncio
import logging
import ssl
import struct
from xml.etree.ElementTree import Element, SubElement, tostring

from defusedxml.ElementTree import fromstring

from backend.app.core.config import settings
from backend.app.models.domain import Domain

logger = logging.getLogger(__name__)

EPP_NS = "urn:ietf:params:xml:ns:epp-1.0"
DOMAIN_NS = "urn:ietf:params:xml:ns:domain-1.0"
CONTACT_NS = "urn:ietf:params:xml:ns:contact-1.0"


class EppError(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"EPP Error {code}: {message}")


class EppClient:
    def __init__(self):
        self.simulate = settings.epp_simulate
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._connected = False

    async def connect(self) -> None:
        if self.simulate:
            logger.info("EPP simulation mode — skipping connection")
            return

        ssl_ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_ctx.load_cert_chain(settings.epp_cert_path, settings.epp_key_path)

        self._reader, self._writer = await asyncio.open_connection(
            settings.epp_host, settings.epp_port, ssl=ssl_ctx
        )
        greeting = await self._read_frame()
        logger.info("EPP connected: %s", greeting[:200])

        await self._login()
        self._connected = True

    async def disconnect(self) -> None:
        if self._writer and not self.simulate:
            await self._logout()
            self._writer.close()
            await self._writer.wait_closed()
        self._connected = False

    async def _read_frame(self) -> bytes:
        assert self._reader is not None
        header = await self._reader.readexactly(4)
        length = struct.unpack("!I", header)[0] - 4
        return await self._reader.readexactly(length)

    async def _send_frame(self, data: bytes) -> bytes:
        assert self._writer is not None and self._reader is not None
        length = len(data) + 4
        self._writer.write(struct.pack("!I", length) + data)
        await self._writer.drain()
        return await self._read_frame()

    def _build_command(self, command_elem: Element) -> bytes:
        epp = Element("epp", xmlns=EPP_NS)
        cmd = SubElement(epp, "command")
        cmd.append(command_elem)
        return tostring(epp, encoding="unicode", xml_declaration=True).encode()

    async def _login(self) -> None:
        login = Element("login")
        SubElement(login, "clID").text = settings.epp_client_id
        SubElement(login, "pw").text = settings.epp_password
        options = SubElement(login, "options")
        SubElement(options, "version").text = "1.0"
        SubElement(options, "lang").text = "en"
        svcs = SubElement(login, "svcs")
        SubElement(svcs, "objURI").text = DOMAIN_NS
        SubElement(svcs, "objURI").text = CONTACT_NS
        response = await self._send_frame(self._build_command(login))
        self._check_response(response)

    async def _logout(self) -> None:
        logout = Element("logout")
        await self._send_frame(self._build_command(logout))

    def _check_response(self, response_data: bytes) -> Element:
        root = fromstring(response_data)
        result = root.find(f".//{{{EPP_NS}}}result")
        if result is not None:
            code = int(result.get("code", "0"))
            if code >= 2000:
                msg_elem = result.find(f"{{{EPP_NS}}}msg")
                msg = msg_elem.text if msg_elem is not None and msg_elem.text else "Unknown error"
                raise EppError(code, msg)
        return root

    async def check_domain(self, domain_name: str) -> bool:
        if self.simulate:
            return domain_name not in _SIMULATED_TAKEN_DOMAINS

        check = Element("check")
        domain_check = SubElement(check, "domain:check", xmlns=DOMAIN_NS)
        SubElement(domain_check, "domain:name").text = domain_name
        response = await self._send_frame(self._build_command(check))
        root = self._check_response(response)

        name_elem = root.find(f".//{{{DOMAIN_NS}}}name")
        if name_elem is not None:
            return name_elem.get("avail") == "1"
        return False

    async def create_domain(self, domain: Domain) -> str | None:
        if self.simulate:
            logger.info("EPP simulate: created domain %s", domain.name)
            return f"SIM-{domain.name}"

        create = Element("create")
        domain_create = SubElement(create, "domain:create", xmlns=DOMAIN_NS)
        SubElement(domain_create, "domain:name").text = domain.name
        SubElement(domain_create, "domain:period", unit="y").text = str(domain.registration_period_years)

        if domain.nameservers:
            ns_elem = SubElement(domain_create, "domain:ns")
            for ns in domain.nameservers.split(","):
                SubElement(ns_elem, "domain:hostObj").text = ns.strip()

        SubElement(domain_create, "domain:registrant").text = str(domain.registrant_contact_id)
        auth_info = SubElement(domain_create, "domain:authInfo")
        SubElement(auth_info, "domain:pw").text = domain.epp_auth_code

        response = await self._send_frame(self._build_command(create))
        root = self._check_response(response)

        cr_data = root.find(f".//{{{DOMAIN_NS}}}creData")
        if cr_data is not None:
            name_elem = cr_data.find(f"{{{DOMAIN_NS}}}name")
            return name_elem.text if name_elem is not None else None
        return None

    async def renew_domain(self, domain_name: str, current_expiry: str, years: int) -> bool:
        if self.simulate:
            logger.info("EPP simulate: renewed %s for %d years", domain_name, years)
            return True

        renew = Element("renew")
        domain_renew = SubElement(renew, "domain:renew", xmlns=DOMAIN_NS)
        SubElement(domain_renew, "domain:name").text = domain_name
        SubElement(domain_renew, "domain:curExpDate").text = current_expiry
        SubElement(domain_renew, "domain:period", unit="y").text = str(years)

        response = await self._send_frame(self._build_command(renew))
        self._check_response(response)
        return True

    async def transfer_domain(self, domain_name: str, auth_code: str) -> bool:
        if self.simulate:
            logger.info("EPP simulate: transfer initiated for %s", domain_name)
            return True

        transfer = Element("transfer", op="request")
        domain_transfer = SubElement(transfer, "domain:transfer", xmlns=DOMAIN_NS)
        SubElement(domain_transfer, "domain:name").text = domain_name
        auth_info = SubElement(domain_transfer, "domain:authInfo")
        SubElement(auth_info, "domain:pw").text = auth_code

        response = await self._send_frame(self._build_command(transfer))
        self._check_response(response)
        return True

    async def delete_domain(self, domain_name: str) -> bool:
        if self.simulate:
            logger.info("EPP simulate: deleted %s", domain_name)
            return True

        delete = Element("delete")
        domain_delete = SubElement(delete, "domain:delete", xmlns=DOMAIN_NS)
        SubElement(domain_delete, "domain:name").text = domain_name

        response = await self._send_frame(self._build_command(delete))
        self._check_response(response)
        return True


_SIMULATED_TAKEN_DOMAINS = {
    "google.com", "amazon.com", "facebook.com", "apple.com", "microsoft.com",
    "github.com", "stackoverflow.com", "reddit.com", "twitter.com", "youtube.com",
}
