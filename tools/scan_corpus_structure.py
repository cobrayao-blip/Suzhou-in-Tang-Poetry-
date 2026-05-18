# -*- coding: utf-8 -*-
"""
扫描篇题错位、句编卷等问题。
输出 index/corpus_structure_report.json

用法:
  python tools/scan_corpus_structure.py
  python tools/scan_corpus_structure.py --fix-safe   # 自动修复明确错位
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from corpus_paths import CORPUS_DIR, INDEX_DIR, ROOT

BOLD_RE = re.compile(r'<p\s+class="Bold">([^<]*)</p>', re.I)
QUOT_RE = re.compile(r'<p\s+class="Quotation">([^<]*)</p>', re.I)
TEXT_RE = re.compile(r'<p\s+class="Text">([^<]*)</p>', re.I)
POETRY_RE = re.compile(r'<p\s+class="PoetryText">([^<]*)</p>', re.I)
TITLE_INNER_RE = re.compile(
    r"^卷\s*(\d+)\s*_\s*(\d+)\s*【([^】]*)】\s*(.*)$"
)
PURE_TITLE_RE = re.compile(r"^卷\s*\d+\s*_\s*\d+\s*【[^】]*】\s*$")


def juan_from_file(name: str) -> int | None:
    m = re.match(r"text(\d+)\.html$", name, re.I)
    return int(m.group(1)) if m else None


def scan_file(fp: Path) -> dict:
    raw = fp.read_text(encoding="utf-8", errors="replace")
    expected = juan_from_file(fp.name)
    rel = f"quantangshi/{fp.name}"
    issues: list[dict] = []

    n_bold = len(BOLD_RE.findall(raw))
    n_poetry = len(POETRY_RE.findall(raw))
    n_text = len(TEXT_RE.findall(raw))
    poetry_ratio = n_poetry / max(1, n_bold + n_poetry + n_text)

    is_jubian = (
        n_poetry > 20
        or (poetry_ratio > 0.35 and n_poetry > 5)
        or re.search(r'<p class="Bold">句</p>', raw) is not None
        or "句编" in raw[:2000]
    )

    for tag, regex in (
        ("Quotation", QUOT_RE),
        ("Text", TEXT_RE),
        ("PoetryText", POETRY_RE),
    ):
        for m in regex.finditer(raw):
            inner = m.group(1).strip()
            tm = TITLE_INNER_RE.match(inner)
            if not tm:
                continue
            juan_n, seq, bracket, tail = int(tm.group(1)), int(tm.group(2)), tm.group(3), tm.group(4).strip()
            kind = "title_wrong_tag"
            detail: dict = {
                "tag": tag,
                "raw": inner,
                "juan_in_title": juan_n,
                "seq": seq,
                "bracket": bracket,
                "tail": tail,
            }
            if expected is not None and juan_n != expected:
                detail["juan_mismatch_file"] = expected
            if tag == "Quotation" and tail:
                kind = "title_and_author_merged_in_quotation"
            elif tag == "Quotation":
                kind = "title_in_quotation"
            elif tag == "Text" and PURE_TITLE_RE.match(inner):
                kind = "title_in_text_only"
            elif tag == "Text":
                kind = "title_mixed_in_text"
            issues.append({"kind": kind, **detail})

    # Bold 仅为作者名（2-4字无【）且下一首结构异常 — 抽样由 title_in_quotation 覆盖

    ju_bian_entries = len(re.findall(r"【句】", raw))

    return {
        "source_file": rel,
        "expected_juan": expected,
        "is_jubian_volume": is_jubian,
        "jubian_marker_count": ju_bian_entries,
        "poetry_text_lines": n_poetry,
        "poetry_text_ratio": round(poetry_ratio, 3),
        "issues": issues,
    }


def fix_safe_file(fp: Path) -> int:
    raw = fp.read_text(encoding="utf-8", errors="replace")
    n = 0

    def repl_text_pure(m: re.Match[str]) -> str:
        nonlocal n
        inner = m.group(1).strip()
        if PURE_TITLE_RE.match(inner):
            n += 1
            return f'<p class="Bold">{inner}</p>'
        return m.group(0)

    raw = TEXT_RE.sub(repl_text_pure, raw)

    def repl_quot_title_author(m: re.Match[str]) -> str:
        nonlocal n
        inner = m.group(1).strip()
        tm = TITLE_INNER_RE.match(inner)
        if not tm or not tm.group(4).strip():
            return m.group(0)
        title_part = inner[: inner.index("】") + 1]
        author = tm.group(4).strip()
        if len(author) > 8 or "，" in author:
            return m.group(0)
        n += 1
        return f'<p class="Bold">{title_part}</p>\n<p class="Quotation">{author}</p>'

    raw = QUOT_RE.sub(repl_quot_title_author, raw)

    # Quotation 仅篇题、下一行 Bold 为短作者名 → 互换为 Bold 篇题 + Quotation 作者
    lines = raw.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        mq = re.match(r'(\s*)<p class="Quotation">([^<]*)</p>\s*$', line)
        if mq and i + 1 < len(lines):
            inner = mq.group(2).strip()
            if TITLE_INNER_RE.match(inner) and not TITLE_INNER_RE.match(inner).group(4).strip():
                mb = re.match(r'\s*<p class="Bold">([^<]*)</p>\s*$', lines[i + 1])
                if mb:
                    author_cand = mb.group(1).strip()
                    if (
                        author_cand
                        and "【" not in author_cand
                        and "卷" not in author_cand
                        and len(author_cand) <= 8
                    ):
                        n += 1
                        out.append(f'{mq.group(1)}<p class="Bold">{inner}</p>')
                        out.append(f'{mq.group(1)}<p class="Quotation">{author_cand}</p>')
                        i += 2
                        continue
        out.append(line)
        i += 1
    raw = "\n".join(out)

    if n:
        fp.write_text(raw, encoding="utf-8")
    return n


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fix-safe", action="store_true")
    parser.add_argument(
        "--json",
        type=Path,
        default=INDEX_DIR / "corpus_structure_report.json",
    )
    args = parser.parse_args()

    reports: list[dict] = []
    fix_total = 0
    for fp in sorted(CORPUS_DIR.glob("text*.html")):
        if args.fix_safe:
            fix_total += fix_safe_file(fp)
        reports.append(scan_file(fp))

    with_issues = [r for r in reports if r["issues"]]
    jubian_vols = [r for r in reports if r["is_jubian_volume"]]

    by_kind: dict[str, int] = {}
    for r in with_issues:
        for iss in r["issues"]:
            by_kind[iss["kind"]] = by_kind.get(iss["kind"], 0) + 1

    summary = {
        "html_files": len(reports),
        "files_with_title_issues": len(with_issues),
        "jubian_volume_count": len(jubian_vols),
        "issue_kind_counts": by_kind,
        "jubian_volumes": [
            {
                "source_file": r["source_file"],
                "poetry_text_lines": r["poetry_text_lines"],
                "poetry_text_ratio": r["poetry_text_ratio"],
                "jubian_marker_count": r["jubian_marker_count"],
            }
            for r in jubian_vols
        ],
        "files_with_issues": with_issues,
    }

    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"已扫描 {len(reports)} 卷")
    print(f"篇题错位涉及 {len(with_issues)} 个文件，共 {sum(by_kind.values())} 处")
    print("类型:", by_kind)
    print(f"句编/摘录体例卷 {len(jubian_vols)} 个")
    if args.fix_safe:
        print(f"已自动修复 {fix_total} 处")
    print("报告:", args.json.relative_to(ROOT))
    return 0 if not with_issues else 2


if __name__ == "__main__":
    raise SystemExit(main())
