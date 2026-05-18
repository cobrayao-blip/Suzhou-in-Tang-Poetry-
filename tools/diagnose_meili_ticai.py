# -*- coding: utf-8 -*-
"""对比 JSONL / PostgreSQL / Meilisearch 体裁统计。"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from build_meilisearch_index import is_parse_error_note
from corpus_paths import INDEX_DIR

JSONL = INDEX_DIR / "quatangshi_phase1.jsonl"
DA = "杂曲歌辞"
MEILI_HOST = os.environ.get("MEILI_HOST", "http://127.0.0.1:7700")
MEILI_KEY = os.environ.get("MEILI_API_KEY", "dev-master-key-change-me")
MEILI_INDEX = os.environ.get("MEILI_INDEX", "quatangshi")


def load_jsonl_stats() -> dict:
    total = 0
    by_da = Counter()
    by_da_clean = Counter()
    da_empty_geci_in_pt = 0
    da_match = 0
    for line in JSONL.open(encoding="utf-8"):
        r = json.loads(line)
        total += 1
        da = (r.get("ticai_da") or "").strip()
        pt = r.get("pian_ti") or ""
        note = r.get("parse_note") or ""
        by_da[da or "(empty)"] += 1
        err = is_parse_error_note(note)
        if da == DA:
            da_match += 1
            if not err:
                by_da_clean[DA] += 1
        if not da and "杂曲歌辞" in pt:
            da_empty_geci_in_pt += 1
    return {
        "total": total,
        "by_da_match": da_match,
        "by_da_clean": by_da_clean[DA],
        "da_empty_geci_in_pt": da_empty_geci_in_pt,
    }


def pg_counts() -> dict | None:
    try:
        import psycopg2
    except ImportError:
        return None
    url = os.environ.get(
        "DATABASE_URL",
        "postgresql://qts:qts_dev_change_me@127.0.0.1:5432/quatangshi",
    )
    conn = psycopg2.connect(url)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM poems")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM poems WHERE ticai_da=%s", (DA,))
    da = cur.fetchone()[0]
    cur.execute(
        """
        SELECT COUNT(*) FROM poems WHERE ticai_da=%s
        AND (
          trim(coalesce(parse_note,'')) = ''
          OR parse_note = 'author_inferred_from_volume'
        )
        """,
        (DA,),
    )
    da_clean = cur.fetchone()[0]
    cur.execute(
        "SELECT COUNT(*) FROM poems WHERE pian_ti LIKE %s AND (ticai_da IS NULL OR trim(ticai_da)='')",
        ("%杂曲歌辞%",),
    )
    pt_only = cur.fetchone()[0]
    conn.close()
    return {
        "total": total,
        "ticai_da": da,
        "ticai_da_clean": da_clean,
        "pian_ti_only": pt_only,
    }


def meili_search(filter_expr: str, q: str = "") -> dict:
    import meilisearch

    client = meilisearch.Client(MEILI_HOST, MEILI_KEY or None)
    index = client.index(MEILI_INDEX)
    stats = index.get_stats()
    params = {"limit": 0, "offset": 0}
    if filter_expr:
        params["filter"] = filter_expr
    result = index.search(q, params)
    return {
        "numberOfDocuments": stats.number_of_documents,
        "estimatedTotalHits": result.get("estimatedTotalHits")
        or result.get("totalHits")
        or 0,
        "processingTimeMs": result.get("processingTimeMs"),
    }


def main() -> int:
    print("=== JSONL ===")
    j = load_jsonl_stats()
    for k, v in j.items():
        print(f"  {k}: {v}")

    print("\n=== PostgreSQL (meta 下拉来源) ===")
    pg = pg_counts()
    if pg is None:
        print("  (跳过: 无 psycopg2)")
    else:
        for k, v in pg.items():
            print(f"  {k}: {v}")

    print("\n=== Meilisearch (检索结果来源) ===")
    try:
        base = meili_search("")
        print(f"  index documents: {base['numberOfDocuments']}")
        print(f"  search all (no filter): hits={base['estimatedTotalHits']}")

        f_da = f'ticai_da = "{DA}"'
        r1 = meili_search(f_da)
        print(f'  filter ticai_da="{DA}": hits={r1["estimatedTotalHits"]}')

        r2 = meili_search(f"{f_da} AND has_parse_note = false")
        print(f"  + has_parse_note=false: hits={r2['estimatedTotalHits']}")

        r3 = meili_search('has_parse_note = false')
        print(f"  has_parse_note=false only: hits={r3['estimatedTotalHits']}")

        # 篇题含杂曲歌辞但 ticai_da 可能为空
        r4 = meili_search(f'pian_ti CONTAINS "{DA}"')
        print(f'  pian_ti CONTAINS "{DA}": hits={r4["estimatedTotalHits"]}')

    except Exception as e:
        print(f"  错误: {e}")
        print("  请确认 Meilisearch 已启动且 MEILI_API_KEY 正确")
        return 1

    print("\n=== 结论提示 ===")
    if pg and base["numberOfDocuments"] != pg["total"]:
        print(
            f"  Meili 文档数 {base['numberOfDocuments']} != PG {pg['total']} → 导入不完整或未同步"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
