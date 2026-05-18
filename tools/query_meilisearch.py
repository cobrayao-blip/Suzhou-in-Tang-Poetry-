# -*- coding: utf-8 -*-
"""在 Meilisearch 中检索全唐诗 Phase 1 索引。用法：python tools/query_meilisearch.py 姑苏"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

MEILI_HOST = os.environ.get("MEILI_HOST", "http://127.0.0.1:7700")
MEILI_API_KEY = os.environ.get("MEILI_API_KEY", "")
MEILI_INDEX = os.environ.get("MEILI_INDEX", "quatangshi")


def main() -> int:
    parser = argparse.ArgumentParser(description="查询 Meilisearch 全唐诗索引")
    parser.add_argument("q", help="检索词")
    parser.add_argument("-n", "--limit", type=int, default=10, help="返回条数")
    parser.add_argument(
        "--filter",
        default="",
        help='Meilisearch 过滤表达式，如 zuo_zhe = "刘长卿"',
    )
    args = parser.parse_args()

    try:
        import meilisearch
    except ImportError:
        print("请安装：pip install -r requirements-search.txt", file=sys.stderr)
        return 1

    client = meilisearch.Client(MEILI_HOST, MEILI_API_KEY or None)
    index = client.index(MEILI_INDEX)
    params: dict = {"limit": args.limit}
    if args.filter:
        params["filter"] = args.filter
    result = index.search(args.q, params)
    hits = result.get("hits", [])
    print(f"命中 {len(hits)} 条（processingTimeMs={result.get('processingTimeMs')}）\n")
    for i, h in enumerate(hits, 1):
        pt = h.get("pian_ti", "")
        zz = h.get("zuo_zhe", "")
        jm = h.get("juan_ming", "")
        body = (h.get("zheng_wen") or "")[:80].replace("\n", " ")
        print(f"{i}. [{jm}] {pt} — {zz}")
        print(f"   {body}…\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
