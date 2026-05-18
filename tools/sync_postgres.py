# -*- coding: utf-8 -*-
"""
将 Phase 1 索引同步到 PostgreSQL（poems 表）。

环境变量：DATABASE_URL
  默认 postgresql://qts:qts_dev_change_me@127.0.0.1:5432/quatangshi

用法：
  docker compose up -d
  python tools/build_phase1_index.py
  python tools/sync_postgres.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from corpus_paths import INDEX_DIR

JSONL_PATH = INDEX_DIR / "quatangshi_phase1.jsonl"
DEFAULT_URL = "postgresql://qts:qts_dev_change_me@127.0.0.1:5432/quatangshi"

COLUMNS = (
    "id",
    "source_file",
    "juan_ming",
    "pian_ti",
    "zuo_zhe",
    "zheng_wen",
    "ticai_da",
    "ticai_xiao",
    "kuohao_nei",
    "parse_note",
)


def load_rows(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            for key in COLUMNS:
                val = row.get(key)
                if val is None:
                    row[key] = ""
            rows.append(row)
    return rows


def main() -> int:
    if not JSONL_PATH.is_file():
        print("未找到:", JSONL_PATH, file=sys.stderr)
        print("请先运行: python tools/build_phase1_index.py", file=sys.stderr)
        return 1

    try:
        import psycopg2
        from psycopg2.extras import execute_values
    except ImportError:
        print("请安装: pip install psycopg2-binary", file=sys.stderr)
        return 1

    url = os.environ.get("DATABASE_URL", DEFAULT_URL)
    rows = load_rows(JSONL_PATH)
    if not rows:
        print("JSONL 无记录", file=sys.stderr)
        return 1

    schema_sql = (_TOOLS.parent / "db" / "schema.sql").read_text(encoding="utf-8")

    conn = psycopg2.connect(url)
    try:
        with conn.cursor() as cur:
            cur.execute(schema_sql)
            cur.execute("TRUNCATE poems CASCADE")
            values = [tuple(row[c] for c in COLUMNS) for row in rows]
            cols = ", ".join(COLUMNS)
            template = f"({', '.join(['%s'] * len(COLUMNS))}, NOW())"
            execute_values(
                cur,
                f"INSERT INTO poems ({cols}, synced_at) VALUES %s",
                values,
                template=template,
                page_size=500,
            )
        conn.commit()
        print(f"已同步 {len(rows)} 条至 PostgreSQL")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
