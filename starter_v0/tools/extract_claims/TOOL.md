---
name: extract_claims
track: bonus
kind: local_formatter
requires_env: []
inputs: [items]
outputs: [claims, claim_count]
side_effect: false
---
# extract_claims

Extracts non-empty claims from already-collected research items and preserves each item's source or URL. It does not fetch or verify claims.
