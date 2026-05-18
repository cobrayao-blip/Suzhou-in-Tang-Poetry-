# -*- coding: utf-8 -*-
"""
扫描无作者条目，区分体例性缺失与疑似漏标。
输出 index/missing_author_report.json

用法:
  python tools/build_phase1_index.py   # 建议先重建索引
  python tools/scan_missing_author.py
"""
from __future__ import annotations

import json
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from build_phase1_index import (
    AUTHOR_INFERRED_NOTE,
    is_new_poem_title_start,
    tokenize_file,
    unescape,
)
from corpus_paths import CORPUS_DIR, INDEX_DIR, ROOT

DB_PATH = INDEX_DIR / "quatangshi_phase1.sqlite"
OUT_PATH = INDEX_DIR / "missing_author_report.json"

GECI_TICAI = frozenset(
    {
        "郊庙歌辞",
        "乐府",
        "相和歌辞",
        "琴曲歌辞",
        "舞曲歌辞",
        "杂歌谣辞",
    }
)


def is_geci_pian_ti(pian_ti: str, ticai_da: str | None) -> bool:
    da = ticai_da or ""
    pt = pian_ti or ""
    if da in GECI_TICAI:
        return True
    if "歌辞" in pt and da != "杂曲歌辞":
        return True
    # 如【明皇祀圜丘乐章·豫和】无「郊庙歌辞」大类前缀
    if any(k in pt for k in ("乐章", "郊庙", "祀昊天", "祀圜丘", "享天乐章", "舞初")):
        return True
    return False


def classify_row(row: sqlite3.Row) -> str:
    note = row["parse_note"] or ""
    if AUTHOR_INFERRED_NOTE in note:
        return "inferred_from_volume"
    if note == "orphan_prose_block":
        return "orphan_prose"
    if note in ("non_title_bold_or_fragment", "no_body", "no_body_no_author"):
        return "parse_fragment"
    da = row["ticai_da"] or ""
    pt = row["pian_ti"] or ""
    if is_geci_pian_ti(pt, da):
        return "corpus_geci"
    if "【句】" in pt:
        return "corpus_jubian"
    if is_new_poem_title_start(pt) and (row["zheng_wen"] or "").strip():
        return "suspected_missing_markup"
    return "other_no_author"


def html_missing_quotation_after_title(fp: Path) -> list[dict]:
    """HTML 层：篇题 Bold 后紧跟 Text（无 Quotation/Bold 作者）。"""
    rel = f"quantangshi/{fp.name}"
    issues: list[dict] = []
    events = tokenize_file(fp)
    i = 0
    while i < len(events):
        kind, text = events[i]
        if kind != "bold":
            i += 1
            continue
        title = unescape(text)
        if not is_new_poem_title_start(title):
            i += 1
            continue
        j = i + 1
        has_quotation = False
        has_author_bold = False
        while j < len(events):
            nk, _ = events[j]
            if nk == "h1":
                break
            if nk == "bold" and is_new_poem_title_start(unescape(events[j][1])):
                break
            if nk == "quotation":
                has_quotation = True
                break
            if nk == "bold":
                has_author_bold = True
                break
            if nk in ("text", "poetry_text"):
                break
            j += 1
        if not has_quotation and not has_author_bold:
            row = {
                "source_file": rel,
                "pian_ti": title,
                "kind": "html_no_quotation_after_title",
            }
            da_m = re.search(r"【([^】]*)】", title)
            if da_m:
                inner = da_m.group(1)
                if "·" in inner:
                    row["ticai_da"] = inner.split("·", 1)[0].strip()
                else:
                    row["ticai_da"] = inner.strip()
            issues.append(row)
        i += 1
    return issues


def file_author_stats(con: sqlite3.Connection) -> dict[str, dict]:
    stats: dict[str, dict] = {}
    for row in con.execute(
        """
        SELECT source_file,
               SUM(CASE WHEN trim(zuo_zhe) != '' THEN 1 ELSE 0 END) AS with_author,
               SUM(CASE WHEN trim(zuo_zhe) = '' THEN 1 ELSE 0 END) AS without_author,
               COUNT(*) AS total
        FROM poems
        WHERE pian_ti LIKE '卷%【%'
        GROUP BY source_file
        """
    ):
        stats[row["source_file"]] = dict(row)
    return stats


def main() -> int:
    if not DB_PATH.is_file():
        print("未找到索引，请先运行: python tools/build_phase1_index.py", file=sys.stderr)
        return 1

    con = sqlite3.connect(str(DB_PATH))
    con.row_factory = sqlite3.Row
    total = con.execute("SELECT COUNT(*) FROM poems").fetchone()[0]
    no_author = con.execute(
        "SELECT COUNT(*) FROM poems WHERE trim(zuo_zhe) = ''"
    ).fetchone()[0]
    inferred = con.execute(
        "SELECT COUNT(*) FROM poems WHERE parse_note LIKE ?",
        (f"%{AUTHOR_INFERRED_NOTE}%",),
    ).fetchone()[0]

    kind_counts: Counter[str] = Counter()
    by_file_suspected: Counter[str] = Counter()
    samples: dict[str, list] = {k: [] for k in (
        "suspected_missing_markup",
        "corpus_geci",
        "corpus_jubian",
        "orphan_prose",
        "other_no_author",
    )}

    fstats = file_author_stats(con)

    for row in con.execute(
        """
        SELECT id, source_file, juan_ming, pian_ti, parse_note,
               ticai_da, ticai_xiao, zheng_wen,
               substr(zheng_wen, 1, 60) AS body_preview
        FROM poems
        WHERE trim(zuo_zhe) = ''
        """
    ):
        kind = classify_row(row)
        kind_counts[kind] += 1
        if kind == "suspected_missing_markup":
            by_file_suspected[row["source_file"]] += 1
        if kind in samples and len(samples[kind]) < 12:
            samples[kind].append(
                {
                    "id": row["id"],
                    "source_file": row["source_file"],
                    "juan_ming": row["juan_ming"],
                    "pian_ti": row["pian_ti"],
                    "parse_note": row["parse_note"],
                    "ticai_da": row["ticai_da"],
                    "body_preview": row["body_preview"],
                }
            )

    # 同卷混有/无作者（诗人别集漏标信号）
    mixed_volume_files: list[dict] = []
    for sf, st in sorted(fstats.items(), key=lambda x: -x[1]["without_author"]):
        wa, wo, t = st["with_author"], st["without_author"], st["total"]
        if wo == 0 or wa == 0:
            continue
        if wo >= 3 and wa >= 3:
            mixed_volume_files.append(
                {
                    "source_file": sf,
                    "with_author": wa,
                    "without_author": wo,
                    "suspected_in_file": by_file_suspected.get(sf, 0),
                }
            )

    html_issues: list[dict] = []
    for fp in sorted(CORPUS_DIR.glob("text*.html")):
        html_issues.extend(html_missing_quotation_after_title(fp))

    # 去掉歌辞体例（与索引分类一致）
    html_suspected = [
        x
        for x in html_issues
        if not is_geci_pian_ti(x.get("pian_ti") or "", x.get("ticai_da"))
        and "【句】" not in (x.get("pian_ti") or "")
    ]

    report = {
        "html_files": len(list(CORPUS_DIR.glob("text*.html"))),
        "index_total": total,
        "index_no_author": no_author,
        "index_no_author_pct": round(100 * no_author / max(1, total), 2),
        "index_inferred_author": inferred,
        "kind_counts": dict(kind_counts),
        "mixed_author_volume_files": mixed_volume_files[:40],
        "top_files_suspected_missing": [
            {"source_file": k, "count": v}
            for k, v in by_file_suspected.most_common(20)
        ],
        "html_no_quotation_after_title_count": len(html_issues),
        "html_suspected_missing_count": len(html_suspected),
        "samples": samples,
        "html_suspected_samples": html_suspected[:20],
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"索引条数: {total}")
    print(f"无作者: {no_author} ({report['index_no_author_pct']}%)")
    print(f"卷内继承已标注: {inferred}")
    print("分类:", dict(kind_counts))
    print(f"HTML 篇题后无 Quotation: {len(html_issues)}（疑似漏标 {len(html_suspected)}）")
    print(f"同卷混有/无作者文件: {len(mixed_volume_files)}")
    print("报告:", OUT_PATH.relative_to(ROOT))
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
