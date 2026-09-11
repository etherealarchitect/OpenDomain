#!/usr/bin/env python3
"""Export the canonical OpenAPI contract used by the public documentation site."""

from __future__ import annotations

import json
from pathlib import Path

from backend.app.main import app

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "website" / "static" / "openapi.json"


def main() -> None:
    schema = app.openapi()
    schema["info"]["description"] = (
        "OpenDomain API. Browser authentication uses email verification, TOTP MFA, "
        "and an opaque HttpOnly session cookie. New registrar and payment features "
        "remain sandbox-gated until provider approval and production readiness checks pass."
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Exported {len(schema['paths'])} OpenAPI paths to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
