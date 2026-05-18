# -*- coding: utf-8 -*-
"""
重建 Phase 1 索引、同步 PostgreSQL、全量重建 Meilisearch。

用法:
  python tools/rebuild_all.py
  python tools/rebuild_all.py --diagnose   # 结束后对比 JSONL / PG / Meili
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(argv: list[str]) -> None:
    print("+", " ".join(argv), flush=True)
    proc = subprocess.run(argv, cwd=ROOT)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)


def main() -> int:
    parser = argparse.ArgumentParser(description="一键重建索引与检索")
    parser.add_argument(
        "--diagnose",
        action="store_true",
        help="结束后运行 diagnose_meili_ticai.py",
    )
    args = parser.parse_args()
    py = sys.executable

    run([py, "tools/build_phase1_index.py"])
    run([py, "tools/sync_postgres.py"])
    run([py, "tools/build_meilisearch_index.py", "--recreate"])
    if args.diagnose:
        run([py, "tools/diagnose_meili_ticai.py"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
