from __future__ import annotations

from typing import Any


def deduplicate_items(
    items: list[dict[str, Any]] | None = None,
    key: str = "url",
) -> dict[str, Any]:
    """Remove repeated research items while preserving their first occurrence."""
    if items is None:
        return {"tool": "deduplicate_items", "items": [], "removed_count": 0}
    if not isinstance(items, list):
        return {"tool": "deduplicate_items", "error": "items_must_be_list"}
    if key not in {"url", "title"}:
        return {"tool": "deduplicate_items", "error": "invalid_key"}

    unique: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in items:
        if not isinstance(item, dict):
            continue
        value = str(item.get(key) or "").strip().casefold()
        if not value or value in seen:
            continue
        seen.add(value)
        unique.append(item)
    return {
        "tool": "deduplicate_items",
        "items": unique,
        "removed_count": len(items) - len(unique),
    }
