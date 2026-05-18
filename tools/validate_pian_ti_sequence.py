# -*- coding: utf-8 -*-
"""
排查各卷 HTML 中篇题序号「卷{卷号}_{序号}【」的连续性。
检查：跳号、重复、卷号与文件名不一致、篇题误标在 Text/Quotation 等。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from corpus_paths import CORPUS_DIR, INDEX_DIR, ROOT

TEXT_FILE_RE = re.compile(r"text(\d+)\.html$", re.I)
BOLD_RE = re.compile(r'<p\s+class="Bold">([^<]*)</p>', re.I)
OTHER_TITLE_RE = re.compile(
    r'<p\s+class="(?:Text|Quotation|PoetryText)">([^<]*卷\s*[\d_]*\s*_\s*[\d_]*\s*【[^<]*)</p>',
    re.I,
)
# 卷164_12【 / 卷_12【 / 卷164_【
PREFIX_RE = re.compile(
    r"^卷\s*(\d+)\s*_\s*(\d+)\s*【"
    r"|^卷\s*_\s*(\d+)\s*【"
    r"|^卷\s*(\d+)\s*_\s*【"
)


@dataclass
class TitleEntry:
    seq: int | None
    juan_in_title: int | None
    raw: str
    tag: str
    line_hint: int


@dataclass
class FileReport:
    source_file: str
    expected_juan: int
    entries: list[TitleEntry] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)


def parse_title(inner: str, tag: str) -> TitleEntry | None:
    inner = inner.strip()
    m = PREFIX_RE.match(inner)
    if not m:
        return None
    if m.group(1) is not None:
        return TitleEntry(
            int(m.group(2)), int(m.group(1)), inner, tag, 0
        )
    if m.group(3) is not None:
        return TitleEntry(int(m.group(3)), None, inner, tag, 0)
    if m.group(4) is not None:
        return TitleEntry(None, int(m.group(4)), inner, tag, 0)
    return None


def scan_file(fp: Path) -> FileReport | None:
    m = TEXT_FILE_RE.match(fp.name)
    if not m:
        return None
    expected_juan = int(m.group(1))
    rel = f"quantangshi/{fp.name}"
    raw = fp.read_text(encoding="utf-8", errors="replace")

    entries: list[TitleEntry] = []
    for tag_re, tag in ((BOLD_RE, "Bold"), (OTHER_TITLE_RE, "other")):
        for mo in tag_re.finditer(raw):
            te = parse_title(mo.group(1), tag)
            if te:
                entries.append(te)

    report = FileReport(rel, expected_juan, entries)
    if not entries:
        return report

    # 卷号与文件名
    for e in entries:
        if e.juan_in_title is not None and e.juan_in_title != expected_juan:
            report.issues.append(
                f"卷号不符: 文件应为卷{expected_juan}，篇题为「{e.raw[:60]}…」"
                if len(e.raw) > 60
                else f"卷号不符: 文件应为卷{expected_juan}，篇题为「{e.raw}」"
            )
        if e.tag != "Bold":
            report.issues.append(f"篇题不在 Bold（{e.tag}）: {e.raw[:80]}")

    numbered = [e for e in entries if e.seq is not None and e.juan_in_title == expected_juan]
    if not numbered and any(e.seq is not None for e in entries):
        numbered = [e for e in entries if e.seq is not None]

    missing_juan = [e for e in entries if e.juan_in_title is None and e.seq is not None]
    if missing_juan:
        report.issues.append(f"缺卷号前缀（卷_序号）: {len(missing_juan)} 处")

    missing_seq = [e for e in entries if e.seq is None and e.juan_in_title == expected_juan]
    if missing_seq:
        report.issues.append(f"缺篇内序号（卷{{n}}_【）: {len(missing_seq)} 处")

    if numbered:
        seqs = [e.seq for e in numbered]
        # 重复
        seen: dict[int, int] = {}
        for s in seqs:
            seen[s] = seen.get(s, 0) + 1
        dups = [s for s, c in seen.items() if c > 1]
        if dups:
            report.issues.append(f"序号重复: {sorted(dups)}")

        sorted_unique = sorted(set(seqs))
        if sorted_unique[0] != 1:
            report.issues.append(
                f"未从 1 起编: 最小序号 {sorted_unique[0]}，最大 {sorted_unique[-1]}，共 {len(seqs)} 篇"
            )

        # 跳号
        gaps: list[str] = []
        for i in range(len(sorted_unique) - 1):
            a, b = sorted_unique[i], sorted_unique[i + 1]
            if b - a > 1:
                missing = list(range(a + 1, b))
                gaps.append(f"{a}→{b}（缺 {missing}）")
        if gaps:
            report.issues.append("序号断档: " + "; ".join(gaps))

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="篇题序号连续性排查")
    parser.add_argument(
        "--json",
        type=Path,
        default=INDEX_DIR / "pian_ti_sequence_report.json",
        help="写入 JSON 报告路径（默认 index/pian_ti_sequence_report.json）",
    )
    parser.add_argument("--quiet", action="store_true", help="仅输出有问题的文件")
    args = parser.parse_args()

    if not CORPUS_DIR.is_dir():
        print("语料目录不存在:", CORPUS_DIR, file=sys.stderr)
        return 1

    all_reports: list[FileReport] = []
    problem_files = 0
    for fp in sorted(CORPUS_DIR.glob("text*.html")):
        rep = scan_file(fp)
        if rep is None:
            continue
        all_reports.append(rep)
        if rep.issues:
            problem_files += 1
            if not args.quiet:
                print(f"\n=== {rep.source_file}（第{rep.expected_juan}卷）===")
                for issue in rep.issues:
                    print(" ", issue)
                if rep.entries:
                    seqs = [
                        e.seq
                        for e in rep.entries
                        if e.seq is not None
                        and (
                            e.juan_in_title is None
                            or e.juan_in_title == rep.expected_juan
                        )
                    ]
                    if seqs:
                        print(f"  序号样本: {seqs[:20]}{'…' if len(seqs) > 20 else ''}")

    def _kind(issue: str) -> str:
        if issue.startswith("序号断档"):
            return "sequence_gap"
        if issue.startswith("序号重复"):
            return "duplicate_seq"
        if issue.startswith("卷号不符"):
            return "juan_mismatch"
        if issue.startswith("缺卷号前缀"):
            return "missing_juan_prefix"
        if issue.startswith("缺篇内序号"):
            return "missing_seq"
        if issue.startswith("篇题不在"):
            return "title_wrong_tag"
        if issue.startswith("未从"):
            return "not_starting_at_1"
        return "other"

    file_rows = []
    tally: dict[str, int] = {}
    for r in all_reports:
        if not r.issues:
            continue
        kinds = list(dict.fromkeys(_kind(i) for i in r.issues))
        for k in kinds:
            tally[k] = tally.get(k, 0) + 1
        file_rows.append(
            {
                "source_file": r.source_file,
                "expected_juan": r.expected_juan,
                "title_count": len(r.entries),
                "issue_kinds": kinds,
                "issues": r.issues,
            }
        )

    summary = {
        "html_files": len(all_reports),
        "files_with_issues": problem_files,
        "issue_kind_counts": tally,
        "files": file_rows,
    }

    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print()
    print(f"已扫描 HTML: {len(all_reports)} 个")
    print(f"存在问题的卷: {problem_files} 个")
    if tally:
        print("问题类型统计:", ", ".join(f"{k}={v}" for k, v in sorted(tally.items())))
    print("报告:", args.json.relative_to(ROOT))
    return 0 if problem_files == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
