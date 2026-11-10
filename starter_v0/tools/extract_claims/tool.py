from __future__ import annotations

from typing import Any


def extract_claims(items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Keep research items that contain a claim and attach their source."""
    if items is None:
        return {"tool": "extract_claims", "claims": [], "claim_count": 0}
    if not isinstance(items, list):
        return {"tool": "extract_claims", "error": "items_must_be_list"}

    claims: list[dict[str, str]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        text = str(item.get("summary") or item.get("claim") or "").strip()
        if not text:
            continue
        source = str(item.get("source") or item.get("url") or "").strip()
        claims.append({"claim": text, "source": source})
    return {"tool": "extract_claims", "claims": claims, "claim_count": len(claims)}
