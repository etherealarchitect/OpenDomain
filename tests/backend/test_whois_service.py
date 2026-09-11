
import pytest

from backend.app.services.whois_service import WhoisResult, WhoisService


@pytest.mark.parametrize(
    "value",
    [
        "https://example.com",
        "example.com/path",
        "example.com:443",
        "127.0.0.1",
        "example.com\n.evil",
        "example.com evil",
        "-example.com",
        "example-.com",
    ],
)
def test_normalize_rejects_unsafe_domain_inputs(value: str) -> None:
    with pytest.raises(ValueError):
        WhoisService.normalize_domain(value)


def test_normalize_accepts_idn_and_trailing_dot() -> None:
    assert WhoisService.normalize_domain("BÜCHER.DE.") == "xn--bcher-kva.de"


def test_malformed_rdap_payload_is_rejected() -> None:
    service = WhoisService()
    with pytest.raises(ValueError):
        service._parse_rdap("example.com", {"status": "not-a-list"})


def test_safe_redirect_rejects_private_hosts_and_changes_of_path() -> None:
    assert WhoisService._safe_redirect(
        "https://rdap.org/domain/example.com", "https://127.0.0.1/domain/example.com", "example.com"
    ) is None
    assert WhoisService._safe_redirect(
        "https://rdap.org/domain/example.com", "https://rdap.example/domain/other.com", "example.com"
    ) is None
    assert WhoisService._safe_redirect(
        "https://rdap.org/domain/example.com", "http://rdap.example/domain/example.com", "example.com"
    ) is None
    assert WhoisService._safe_redirect(
        "https://rdap.org/domain/example.com", "https://localhost/domain/example.com", "example.com"
    ) is None
    assert WhoisService._safe_redirect(
        "https://rdap.org/domain/example.com", "https://rdap.verisign.com/com/v1/domain/example.com", "example.com"
    ) == "https://rdap.verisign.com/com/v1/domain/example.com"


@pytest.mark.asyncio
async def test_lookup_does_not_infer_available_from_failed_sources(monkeypatch: pytest.MonkeyPatch) -> None:
    service = WhoisService()

    async def failed_rdap(domain: str):
        return WhoisResult(domain_name=domain, warnings=["RDAP failed"])

    async def failed_whois(domain: str):
        return WhoisResult(domain_name=domain, warnings=["WHOIS failed"])

    monkeypatch.setattr(service, "_lookup_rdap", failed_rdap)
    monkeypatch.setattr(service, "_lookup_whois", failed_whois)
    result = await service.lookup("example.com")
    assert result.lookup_status == "unknown"
    assert result.source == "none"
    assert not hasattr(service, "_lookup_whois") or result.lookup_status == "unknown"


@pytest.mark.asyncio
async def test_rdap_not_found_is_not_available(monkeypatch: pytest.MonkeyPatch) -> None:
    service = WhoisService()

    async def not_found(domain: str):
        return WhoisResult(domain_name=domain, lookup_status="not_found", source="rdap")

    monkeypatch.setattr(service, "_lookup_rdap", not_found)
    result = await service.lookup("example.com")
    assert result.lookup_status == "not_found"
    assert result.lookup_status != "available"


@pytest.mark.asyncio
async def test_cache_is_bounded_and_normalized(monkeypatch: pytest.MonkeyPatch) -> None:
    service = WhoisService()
    service.MAX_CACHE_ENTRIES = 2

    async def registered(domain: str):
        return WhoisResult(domain_name=domain, lookup_status="registered", source="rdap")

    monkeypatch.setattr(service, "_lookup_rdap", registered)
    for domain in ("one.example", "two.example", "three.example"):
        await service.lookup(domain)
    assert len(service._cache) <= 2
    assert "three.example" in service._cache
