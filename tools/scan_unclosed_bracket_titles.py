# -*- coding: utf-8 -*-
"""
扫描篇题 Bold 中「【」未闭合（缺 】）及错位闭合（】在 Text/次行 Bold）。

  python tools/scan_unclosed_bracket_titles.py
  python tools/scan_unclosed_bracket_titles.py --fix-safe
"""
from __future__ import annotations

import argparse
import html as html_module
import json
import re
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from corpus_paths import CORPUS_DIR, INDEX_DIR, ROOT

OUT_PATH = INDEX_DIR / "unclosed_bracket_report.json"

BOLD_RE = re.compile(r'<p\s+class="Bold"[^>]*>([^<]*)</p>', re.I)
TAG_RE = re.compile(
    r'<p\s+class="Bold"[^>]*>([^<]*)</p>|'
    r'<p\s+class="Text"[^>]*>([^<]*)</p>|'
    r'<p\s+class="Quotation"[^>]*>([^<]*)</p>',
    re.I,
)
TITLE_START = re.compile(r"^\s*卷\s*\d+\s*_\s*\d+\s*【")
UNCLOSED_TITLE_RE = re.compile(r"^卷\s*(\d+)\s*_\s*(\d+)\s*【([^】]*)$")

MAX_SAFE_INNER_LEN = 48
MAX_SAFE_TOTAL_LEN = 64


def unescape(s: str) -> str:
    return html_module.unescape(s.strip())


def classify(inner: str, full: str) -> str:
    if not TITLE_START.match(full):
        return "non_standard_title"
    if len(full) > MAX_SAFE_TOTAL_LEN or len(inner) > MAX_SAFE_INNER_LEN:
        return "likely_truncated"
    if inner.count("【") > 0:
        return "likely_truncated"
    if re.search(r"[…\.]{2,}$", inner):
        return "likely_truncated"
    if len(inner) >= 28 and inner[-1] in "，。、；":
        return "likely_truncated"
    return "safe_missing_close"


def scan_misplaced_close(fp: Path) -> list[dict]:
    """篇题无 】，但紧随的 Text 末或下一 Bold 末带 】。"""
    raw = fp.read_text(encoding="utf-8", errors="replace")
    rel = f"quantangshi/{fp.name}"
    events: list[tuple[str, str]] = []
    for m in TAG_RE.finditer(raw):
        if m.group(1) is not None:
            events.append(("bold", unescape(m.group(1))))
        elif m.group(2) is not None:
            events.append(("text", unescape(m.group(2))))
        elif m.group(3) is not None:
            events.append(("quotation", unescape(m.group(3))))

    issues: list[dict] = []
    i = 0
    while i < len(events):
        kind, text = events[i]
        if kind == "bold" and "【" in text and "】" not in text and TITLE_START.match(text):
            # 下一非 bold 且非 quotation 的 text 以 】 结尾
            if i + 1 < len(events) and events[i + 1][0] == "text":
                nxt = events[i + 1][1]
                if nxt.endswith("】") and "【" not in nxt:
                    issues.append(
                        {
                            "source_file": rel,
                            "kind": "close_bracket_on_following_text",
                            "raw_bold": text,
                            "following_text_tail": nxt[-40:],
                        }
                    )
            # 下一 bold 以 】 结尾（篇题拆两行）
            if i + 1 < len(events) and events[i + 1][0] == "bold":
                nxt = events[i + 1][1]
                if nxt.endswith("】") and "【" not in nxt.split("】")[0]:
                    issues.append(
                        {
                            "source_file": rel,
                            "kind": "split_bold_continuation",
                            "raw_bold": text,
                            "continuation_bold": nxt,
                        }
                    )
        i += 1
    return issues


def scan_file(fp: Path) -> list[dict]:
    issues = scan_misplaced_close(fp)
    raw = fp.read_text(encoding="utf-8", errors="replace")
    rel = f"quantangshi/{fp.name}"
    for m in BOLD_RE.finditer(raw):
        text = unescape(m.group(1))
        if "【" not in text or "】" in text:
            continue
        um = UNCLOSED_TITLE_RE.match(text)
        if um:
            juan_n, seq, bracket_inner = int(um.group(1)), int(um.group(2)), um.group(3)
        else:
            juan_n, seq, bracket_inner = None, None, (
                text.split("【", 1)[-1] if "【" in text else text
            )
        kind = classify(bracket_inner.strip(), text)
        issues.append(
            {
                "source_file": rel,
                "raw_bold": text,
                "juan_in_title": juan_n,
                "seq": seq,
                "bracket_inner": bracket_inner.strip(),
                "kind": kind,
                "suggested_bold": f"{text}】" if kind == "safe_missing_close" else None,
            }
        )
    return issues


def apply_fix_safe(fp: Path, issues: list[dict]) -> int:
    to_fix = [i for i in issues if i["kind"] == "safe_missing_close" and i.get("suggested_bold")]
    if not to_fix:
        return 0
    raw = fp.read_text(encoding="utf-8", errors="replace")
    n = 0
    for item in to_fix:
        old, new = item["raw_bold"], item["suggested_bold"]
        chunk_old, chunk_new = f">{old}</p>", f">{new}</p>"
        if raw.count(chunk_old) != 1:
            continue
        raw = raw.replace(chunk_old, chunk_new, 1)
        n += 1
    if n:
        fp.write_text(raw, encoding="utf-8")
    return n


def main() -> int:
    parser = argparse.ArgumentParser(description="扫描篇题【未闭合")
    parser.add_argument("--fix-safe", action="store_true", help="为短题名补全 】")
    args = parser.parse_args()

    all_issues: list[dict] = []
    by_kind: dict[str, int] = {}
    fixed = 0

    for fp in sorted(CORPUS_DIR.glob("text*.html")):
        file_issues = scan_file(fp)
        if args.fix_safe and file_issues:
            fixed += apply_fix_safe(fp, file_issues)
            file_issues = scan_file(fp)
        all_issues.extend(file_issues)
        for it in file_issues:
            by_kind[it["kind"]] = by_kind.get(it["kind"], 0) + 1

    report = {
        "html_files": len(list(CORPUS_DIR.glob("text*.html"))),
        "issue_count": len(all_issues),
        "by_kind": by_kind,
        "issues": all_issues,
        "fixed_this_run": fixed if args.fix_safe else 0,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"扫描 {report['html_files']} 卷")
    print(f"问题: {report['issue_count']} 处")
    print("分类:", report["by_kind"])
    if args.fix_safe:
        print(f"已自动补 】(短题名): {fixed} 处")
    print("报告:", OUT_PATH.relative_to(ROOT))
    return 0 if report["issue_count"] == 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
