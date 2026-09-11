# agent-qc-kit

**Quality checklist + prompts for agent-generated research and content.**

Built for maintainers and solo operators who ship AI-assisted posts, notes, and docs — and need a repeatable gate so drafts do not invent numbers, drop citations, or sneak in investment advice.

## Why this exists

Agent workflows fail quietly: truncated posts, missing sources, unverifiable stats, soft sell language. This kit is a small, public, maintainer-friendly checklist you can run before publish.

## What's inside

| Path | Purpose |
|------|---------|
| `CHECKLIST.md` | Pre-publish QC gate (copy/paste or automate) |
| `docs/prompts.md` | Maintainer prompts for review / rewrite / cite |
| `examples/sample-pass.md` | Example draft that passes the gate |
| `examples/sample-fail.md` | Example draft that must be rejected |
| `scripts/lint-checklist.sh` | Tiny shell lint for required section headers |

## Quick start

```bash
# 1. Read the gate
cat CHECKLIST.md

# 2. Optional: verify checklist structure
bash scripts/lint-checklist.sh
```

## Maintainer workflow (Codex-friendly)

1. Open an issue with the `qc-review` template.
2. Paste the draft under review.
3. Run through `CHECKLIST.md` — fail any hard rule.
4. Fix or reject; never invent facts to "complete" a draft.
5. Tag a release when checklist semantics change.

## Hard rules (non-negotiable)

- Public sources only; every material claim needs a URL + date when available.
- No fabricated metrics, quotes, or "Source:" labels on invented data.
- No target prices, buy/sell calls, or return promises for securities.
- Prefer deleting a draft over shipping a truncated/garbled post.

## License

MIT — see `LICENSE`.

## Status

Actively maintained. Issues and PRs welcome for checklist clarity and language packs.
