"""Pure validation and comparison helpers for local DNS imports."""

import hashlib
import json
import re

import dns.exception
import dns.name
import dns.rdata
from backend.app.schemas.dns import DnsRecordCreate

PROTECTED_TYPES = {"SOA", "DNSKEY", "DS"}


def normalize_record(record: DnsRecordCreate, zone_name: str) -> DnsRecordCreate:
    origin = dns.name.from_text(zone_name + ".")
    name = record.name.strip().lower()
    if name == zone_name.lower().rstrip("."):
        name = "@"
    try:
        owner = dns.name.from_text(name, origin=origin)
        if not owner.is_subdomain(origin):
            raise ValueError("Record name must belong to this zone")
        relative = owner.relativize(origin).to_text()
        if any(not re.fullmatch(rb"[a-z0-9_*\-]+", label) for label in owner.labels if label):
            raise ValueError("Record name contains unsupported characters")
        content = record.content
        if any(ord(char) < 32 or ord(char) == 127 for char in content):
            raise ValueError("Record content cannot contain control characters")
        record_type = record.record_type
        if record_type in PROTECTED_TYPES:
            raise ValueError("DNSSEC and SOA records cannot be changed through discovery import")
        if record_type == "CNAME" and relative == "@":
            raise ValueError("A zone apex cannot be a CNAME")
        if record_type in {"MX", "SRV"}:
            if record.priority is None:
                raise ValueError(f"{record_type} requires priority")
            content = f"{record.priority} {content}"
        elif record.priority is not None:
            raise ValueError("Priority is only supported for MX and SRV")
        if record_type == "TXT" and not content.startswith('"'):
            content = '"' + content.replace("\\", "\\\\").replace('"', '\\"') + '"'
        parsed = dns.rdata.from_text(
            "IN",
            "CNAME" if record_type == "ALIAS" else record_type,
            content,
            origin=dns.name.root,
            relativize=False,
        )
        content = parsed.to_text()
        if record_type in {"MX", "SRV"}:
            content = content.split(" ", 1)[1]
        if record_type in {"CNAME", "NS", "PTR", "MX", "ALIAS"}:
            content = content.lower()
        return record.model_copy(update={"name": relative, "content": content})
    except dns.exception.DNSException as exc:
        raise ValueError(f"Invalid {record.record_type} record") from exc


def record_key(record) -> tuple:
    # TXT bytes and trailing punctuation are significant; never strip them.
    return (str(record.record_type), record.name, record.content, record.priority)


def record_settings(record) -> tuple:
    return (record.ttl, record.proxied, getattr(record, "enabled", True))


def has_conflict(record, others) -> bool:
    for other in others:
        if record.name != other.name:
            continue
        if "CNAME" in {str(record.record_type), str(other.record_type)} and record_key(
            record
        ) != record_key(other):
            return True
        if record.record_type == other.record_type and record.ttl != other.ttl:
            return True
        if record_key(record) == record_key(other) and record_settings(record) != record_settings(
            other
        ):
            return True
    return False


def zone_revision(zone) -> str:
    if zone is None:
        return hashlib.sha256(b"no-zone").hexdigest()
    rows = sorted(
        (str(record.id), *record_key(record), *record_settings(record), record.comment)
        for record in zone.records
    )
    payload = json.dumps([str(zone.id), zone.serial, rows], separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()
