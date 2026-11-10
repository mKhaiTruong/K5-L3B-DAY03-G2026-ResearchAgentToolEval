---
name: deduplicate_items
track: bonus
kind: local_formatter
requires_env: []
inputs: [items, key]
outputs: [items, removed_count]
side_effect: false
---
# deduplicate_items

Removes repeated research items by URL or title while preserving the first occurrence. It does not fetch, merge, or rank items.
