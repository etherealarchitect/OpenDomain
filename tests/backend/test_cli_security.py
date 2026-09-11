from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

from backend.app import cli


def test_credentials_are_isolated_by_api_origin(tmp_path: Path) -> None:
    first = cli.OpenDomainCLI("https://one.example/api/v1", tmp_path)
    second = cli.OpenDomainCLI("https://two.example/api/v1", tmp_path)

    first._save_token("one-token")

    assert first.token_path != second.token_path
    assert first.token == "one-token"
    assert second.token is None
    assert cli.OpenDomainCLI("https://one.example/api/v1", tmp_path).token == "one-token"


@pytest.mark.parametrize("url", ["http://example.com/api/v1", "ftp://example.com/api/v1", "https://user@example.com/api/v1"])
def test_non_loopback_api_urls_are_rejected(url: str) -> None:
    with pytest.raises(ValueError):
        cli.OpenDomainCLI(url)


@pytest.mark.parametrize("host", ["localhost", "127.0.0.1", "::1"])
def test_loopback_http_is_allowed(host: str) -> None:
    instance = cli.OpenDomainCLI(f"http://[{host}]/api/v1" if ":" in host else f"http://{host}:8000/api/v1")
    assert instance.api_url.startswith("http://")


def test_symlinked_state_path_is_rejected(tmp_path: Path) -> None:
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "state"
    link.symlink_to(real, target_is_directory=True)

    with pytest.raises(OSError):
        cli.OpenDomainCLI("https://example.com/api/v1", link)


def test_token_storage_is_atomic_private_and_updates_memory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    instance = cli.OpenDomainCLI("https://example.com/api/v1", tmp_path)
    calls: list[tuple[Path, Path]] = []
    original_replace = os.replace

    def recording_replace(source: str | os.PathLike[str], destination: str | os.PathLike[str]) -> None:
        calls.append((Path(source), Path(destination)))
        original_replace(source, destination)

    monkeypatch.setattr(cli.os, "replace", recording_replace)
    instance._save_token("secret")

    assert instance.token == "secret"
    assert instance.token_path.read_text() == "secret"
    assert stat.S_IMODE(instance.token_path.stat().st_mode) == 0o600
    assert calls and calls[0][1] == instance.token_path
    assert not list(instance.token_path.parent.glob(".session.*"))


def test_transfer_auth_code_is_prompted_not_parser_argument(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli.sys, "argv", ["opendomain", "transfer", "example.com"])

    class FakeCLI:
        def transfer(self, args: object) -> None:
            assert not hasattr(args, "auth_code")

    monkeypatch.setattr(cli, "OpenDomainCLI", lambda **kwargs: FakeCLI())
    cli.main()
