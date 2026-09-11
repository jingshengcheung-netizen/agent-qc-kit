"""Agent publish gate — fail closed on HARD quality violations."""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ADVICE_RE = re.compile(
    r"(买入|卖出|建仓|加仓|减仓|目标价|必涨|翻倍|稳赚|"
    r"\bbuy\b|\bsell\b|target\s*price|guaranteed\s+return|"
    r"will\s+10x|not\s+financial\s+advice)",
    re.I,
)
# "not investment advice" alone is OK; catch advice-like phrasing without disclaimer later
PURE_ADVICE_RE = re.compile(
    r"(买入|卖出|建仓|加仓|减仓|目标价|必涨|翻倍|稳赚|"
    r"\bbuy\s+now\b|\bsell\s+now\b|target\s*price|"
    r"guaranteed\s+return|will\s+10x)",
    re.I,
)
NUMBER_RE = re.compile(
    r"(?<![A-Za-z/])(?:\$?\d{1,3}(?:,\d{3})+(?:\.\d+)?[BMKbm]?|\$?\d+(?:\.\d+)?%|\$?\d+(?:\.\d+)?[BMKbm]|\d+(?:\.\d+)?(?:亿|万|倍))",
)
URL_RE = re.compile(r"https?://[^\s)>\]]+")
BROKEN_QUOTE_RE = re.compile(r"(」[^「]*$|^[^「]*」|「[^」]*$|^[^「]*」)")
# opening starts mid-word / missing leading char patterns seen in production
TRUNCATED_OPEN_RE = re.compile(
    r"^(业落地|的真卡|不是模型|别只比|大厂把「通用」和)",
)


@dataclass
class Finding:
    rule: str
    severity: str
    detail: str


def check_text(text: str) -> list[Finding]:
    findings: list[Finding] = []
    stripped = text.strip()
    if not stripped:
        return [Finding("empty", "HARD", "Draft is empty")]

    first_line = stripped.splitlines()[0].strip()
    if len(first_line) < 8:
        findings.append(Finding("short_open", "HARD", "First line too short to be a complete judgment"))
    if TRUNCATED_OPEN_RE.search(first_line):
        findings.append(Finding("truncated_open", "HARD", f"First line looks truncated: {first_line[:40]}"))
    if first_line.endswith(("…", "...", "——", "—")) and len(first_line) < 40:
        findings.append(Finding("truncated_open", "HARD", "First line ends mid-thought"))

    # broken CJK quotes
    if stripped.count("「") != stripped.count("」"):
        findings.append(Finding("broken_quotes", "HARD", "Mismatched 「」 quotes"))
    if stripped.count("“") != stripped.count("”"):
        findings.append(Finding("broken_quotes", "HARD", "Mismatched curly quotes"))

    if PURE_ADVICE_RE.search(stripped) and not re.search(r"not investment advice|非投资建议", stripped, re.I):
        findings.append(Finding("investment_advice", "HARD", "Looks like buy/sell or return promise without disclaimer"))

    nums = NUMBER_RE.findall(stripped)
    urls = URL_RE.findall(stripped)
    if nums and not urls:
        findings.append(
            Finding(
                "number_without_source",
                "HARD",
                f"Found numeric claims {nums[:3]} but no http(s) source URL",
            )
        )

    # invented-source smell
    if re.search(r"Source:\s*[A-Za-z].{0,40}$", stripped, re.M) and not urls:
        findings.append(Finding("fake_source_label", "HARD", "Has Source: label but no URL"))

    return findings


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Fail closed QC gate for agent drafts")
    p.add_argument("path", nargs="?", help="File to check (default: stdin)")
    p.add_argument("--strict", action="store_true", help="Treat WARN as fail (reserved)")
    args = p.parse_args(argv)

    if args.path:
        text = Path(args.path).read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()

    findings = check_text(text)
    hard = [f for f in findings if f.severity == "HARD"]
    if not findings:
        print("PASS")
        return 0
    for f in findings:
        print(f"{f.severity}\t{f.rule}\t{f.detail}")
    return 1 if hard else 0


if __name__ == "__main__":
    raise SystemExit(main())
