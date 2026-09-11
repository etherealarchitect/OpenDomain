import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

import dns.rrset
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.app.core.database import Base
from backend.app.models import Domain, User
from backend.app.models.dns import RecordType
from backend.app.schemas.dns import DnsDiscoveryResponse, DnsRecordCreate
from backend.app.services.dns_import import normalize_record, record_key
from backend.app.services.dns_service import DnsRevisionConflictError, DnsService


def record(content="192.0.2.1", **kwargs):
    return DnsRecordCreate(
        **{"record_type": "A", "name": "@", "content": content, **kwargs}
    )


@pytest_asyncio.fixture
async def database():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    async with async_sessionmaker(engine, expire_on_commit=False)() as session:
        user = User(
            email="dns@example.com", hashed_password="not-a-password", full_name="Test"
        )
        session.add(user)
        await session.flush()
        domain = Domain(
            name="example.com",
            tld="com",
            owner_id=user.id,
            registration_date=datetime.now(UTC),
            expiry_date=datetime.now(UTC),
        )
        session.add(domain)
        await session.flush()
        yield session, domain, user
    await engine.dispose()


@pytest.mark.asyncio
async def test_preview_does_not_create_zone(database):
    session, domain, user = database
    service = DnsService(session)
    preview = await service.preview_import(domain.id, [record()], user.id)
    assert len(preview.additions) == 1
    assert await service.get_zone(domain.id, user.id) is None


@pytest.mark.asyncio
async def test_merge_multiple_values_and_deduplicate(database):
    session, domain, user = database
    service = DnsService(session)
    await service.create_record(domain.id, record(), user.id)
    data = [record(), record("192.0.2.2"), record("192.0.2.2")]
    preview = await service.preview_import(domain.id, data, user.id)
    assert len(preview.additions) == len(preview.unchanged) == 1
    assert not preview.conflicts
    zone = await service.apply_import(
        domain.id, data, "merge", False, user.id, preview.revision
    )
    assert sorted(r.content for r in zone.records if r.record_type == RecordType.A) == [
        "192.0.2.1",
        "192.0.2.2",
    ]


@pytest.mark.asyncio
async def test_replace_preserves_ns_and_returns_fresh_records(database):
    session, domain, user = database
    service = DnsService(session)
    await service.create_record(domain.id, record(name="old"), user.id)
    preview = await service.preview_import(domain.id, [record()], user.id)
    with pytest.raises(ValueError, match="confirm_replace"):
        await service.apply_import(
            domain.id, [record()], "replace", False, user.id, preview.revision
        )
    zone = await service.apply_import(
        domain.id, [record()], "replace", True, user.id, preview.revision
    )
    assert len([r for r in zone.records if r.record_type == RecordType.NS]) == 2
    assert all(r.name != "old" for r in zone.records)


@pytest.mark.asyncio
async def test_stale_preview_rejected(database):
    session, domain, user = database
    service = DnsService(session)
    preview = await service.preview_import(domain.id, [record()], user.id)
    await service.create_record(domain.id, record("192.0.2.2"), user.id)
    with pytest.raises(DnsRevisionConflictError):
        await service.apply_import(
            domain.id, [record()], "merge", False, user.id, preview.revision
        )


@pytest.mark.asyncio
async def test_conflicting_merge_does_not_partially_apply(database):
    session, domain, user = database
    service = DnsService(session)
    await service.create_record(domain.id, record(name="www"), user.id)
    data = [
        record("target.example.net", record_type="CNAME", name="www"),
        record(name="new"),
    ]
    preview = await service.preview_import(domain.id, data, user.id)
    assert len(preview.conflicts) == 1
    with pytest.raises(ValueError, match="Merge conflicts"):
        await service.apply_import(
            domain.id, data, "merge", False, user.id, preview.revision
        )
    zone = await service.get_zone(domain.id, user.id)
    assert not any(r.name == "new" for r in zone.records)


@pytest.mark.asyncio
async def test_ownership_before_network_or_mutation(database, monkeypatch):
    session, domain, _ = database
    service = DnsService(session)
    resolver = AsyncMock()
    monkeypatch.setattr("dns.asyncresolver.Resolver", lambda: resolver)
    with pytest.raises(ValueError, match="access denied"):
        await service.discover_records(domain.id, uuid.uuid4())
    resolver.resolve.assert_not_called()
    with pytest.raises(ValueError, match="access denied"):
        await service.preview_import(domain.id, [record()], uuid.uuid4())


@pytest.mark.parametrize(
    "data",
    [
        record("not-an-ip"),
        record(name="outside.example.net."),
        record("target.example.com", record_type="CNAME"),
        record("bad\nvalue", record_type="TXT"),
        record(name="bad name"),
        record("mail.example.com", record_type="MX"),
    ],
)
def test_invalid_records_rejected(data):
    with pytest.raises(ValueError):
        normalize_record(data, "example.com")


def test_txt_punctuation_preserved_and_names_normalized():
    first = normalize_record(
        record("value.", record_type="TXT", name="EXAMPLE.COM."), "example.com"
    )
    second = normalize_record(record("value", record_type="TXT"), "example.com")
    assert first.name == "@"
    assert first.content == '"value."'
    assert record_key(first) != record_key(second)


def test_mx_and_srv_priority_zero_and_low_ttl():
    mx = normalize_record(
        record("MAIL.EXAMPLE.NET", record_type="MX", priority=0, ttl=0), "example.com"
    )
    srv = normalize_record(
        record(
            "5 443 target.example.net", record_type="SRV", name="_x._tcp", priority=0
        ),
        "example.com",
    )
    assert mx.content == "mail.example.net."
    assert mx.priority == mx.ttl == 0
    assert srv.content == "5 443 target.example.net."


def test_input_rrset_ttl_conflict_and_empty_replace_rejected():
    with pytest.raises(ValueError, match="inconsistent"):
        DnsService._normalize_import(
            [record(ttl=60), record("192.0.2.2", ttl=300)], "example.com"
        )
    with pytest.raises(ValueError):
        DnsService._normalize_import([], "example.com")


@pytest.mark.asyncio
async def test_discovery_does_not_relabel_alias_target(database, monkeypatch):
    session, domain, user = database

    class Answer:
        def __init__(self, rrset):
            self.rrset = rrset

        def __iter__(self):
            return iter(self.rrset)

    async def resolve(name, rtype, **kwargs):
        assert name == "example.com." and kwargs["search"] is False
        if rtype == "A":
            return Answer(
                dns.rrset.from_text("target.example.net.", 30, "IN", "A", "192.0.2.1")
            )
        if rtype == "MX":
            return Answer(
                dns.rrset.from_text(
                    "example.com.", 30, "IN", "MX", "0 mail.example.net."
                )
            )
        return SimpleNamespace(rrset=None)

    monkeypatch.setattr(
        "dns.asyncresolver.Resolver", lambda: SimpleNamespace(resolve=resolve)
    )
    discovery = await DnsService(session).discover_records(domain.id, user.id)
    response = DnsDiscoveryResponse.model_validate(discovery, from_attributes=True)
    assert [r.record_type for r in response.records] == ["MX"]
    assert response.records[0].priority == 0
    assert response.records[0].ttl == 30
    assert any("alias-target" in warning for warning in response.warnings)
