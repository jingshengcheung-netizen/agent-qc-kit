# agent-qc-kit

**Fail-closed publish gate for agent-generated research and content.**

Solves a real failure mode: AI drafts that look fine until they ship — truncated openings, buy/sell language, numbers with no source URL, broken quotes. This kit **blocks publish** when HARD rules fail (exit code `1`).

## Problem → fix

| Failure we hit in production | Gate rule |
|------------------------------|-----------|
| First line cut mid-sentence after length limits | `truncated_open` |
| Soft investment advice slipping into “research” posts | `investment_advice` |
| Impressive numbers with no link | `number_without_source` |
| Mismatched `「」` after bad truncation | `broken_quotes` |

## Install / run (no packaging required)

```bash
# from repo root
PYTHONPATH=src python -m agent_qc_kit path/to/draft.md
echo $?   # 0 = PASS, 1 = HARD fail
```

Or pipe stdin:

```bash
pbpaste | PYTHONPATH=src python -m agent_qc_kit
```

## Checklist + prompts

- `CHECKLIST.md` — human gate (same HARD philosophy)
- `docs/prompts.md` — reviewer prompts for Codex / ChatGPT
- `examples/` — pass/fail fixtures used in CI

## CI

GitHub Actions runs unit tests and asserts `sample-fail` exits non-zero / `sample-pass` exits 0.

## Maintainer use (this repo’s purpose)

1. Paste draft into a file or stdin.
2. Run the gate before posting to X / shipping a pack.
3. Fix HARD findings or **do not publish**.
4. Open issues when a new failure mode appears; add a rule + test.

## License

MIT
