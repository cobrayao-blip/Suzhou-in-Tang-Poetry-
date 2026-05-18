# -*- coding: utf-8 -*-
"""
将 Phase 1 索引（index/quatangshi_phase1.jsonl）导入自建 Meilisearch。

环境变量：
  MEILI_HOST      默认 http://127.0.0.1:7700
  MEILI_API_KEY   与 Meilisearch 的 MEILI_MASTER_KEY 一致（开发环境见 docker-compose.yml）
  MEILI_INDEX     默认 quatangshi

用法：
  pip install -r requirements-search.txt
  docker compose up -d
  python tools/build_phase1_index.py
  python tools/build_meilisearch_index.py
  python tools/build_meilisearch_index.py --recreate   # 删除并重建索引
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from corpus_paths import INDEX_DIR, ROOT

JSONL_PATH = INDEX_DIR / "quatangshi_phase1.jsonl"
MEILI_HOST = os.environ.get("MEILI_HOST", "http://127.0.0.1:7700")
MEILI_API_KEY = os.environ.get("MEILI_API_KEY", "dev-master-key-change-me")
MEILI_INDEX = os.environ.get("MEILI_INDEX", "quatangshi")

# parse_note 非空但仍参与默认检索（非结构错误）
_PARSE_NOTE_NON_ERROR = frozenset({"author_inferred_from_volume"})


def is_parse_error_note(parse_note: str) -> bool:
    note = str(parse_note or "").strip()
    if not note:
        return False
    parts = [p.strip() for p in note.split(";") if p.strip()]
    return any(p not in _PARSE_NOTE_NON_ERROR for p in parts)


SEARCHABLE = [
    "zheng_wen",
    "pian_ti",
    "zuo_zhe",
    "juan_ming",
    "ticai_da",
    "ticai_xiao",
    "kuohao_nei",
]
FILTERABLE = [
    "zuo_zhe",
    "juan_ming",
    "source_file",
    "ticai_da",
    "ticai_xiao",
    "has_parse_note",
    "has_author",
]
DISPLAYED = [
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
    "has_parse_note",
    "has_author",
]


def load_documents(path: Path) -> list[dict]:
    docs: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            # Meilisearch 字段宜为标量；空值统一为 ""
            for key in list(row.keys()):
                if row[key] is None:
                    row[key] = ""
            row["has_parse_note"] = is_parse_error_note(row.get("parse_note", ""))
            row["has_author"] = bool(str(row.get("zuo_zhe", "")).strip())
            docs.append(row)
    return docs


def get_client():
    try:
        import meilisearch
    except ImportError as e:
        print(
            "未安装 meilisearch 包。请执行：pip install -r requirements-search.txt",
            file=sys.stderr,
        )
        raise SystemExit(1) from e
    return meilisearch.Client(MEILI_HOST, MEILI_API_KEY or None)


def ensure_index(client, index_uid: str, recreate: bool) -> None:
    if recreate:
        try:
            client.delete_index(index_uid)
        except Exception:
            pass
    try:
        client.get_index(index_uid)
    except Exception:
        client.create_index(index_uid, {"primaryKey": "id"})


def configure_index(index) -> None:
    index.update_searchable_attributes(SEARCHABLE)
    index.update_filterable_attributes(FILTERABLE)
    index.update_displayed_attributes(DISPLAYED)
    index.update_settings({"pagination": {"maxTotalHits": 50000}})


def upload_batches(index, docs: list[dict], batch_size: int = 1000) -> None:
    for i in range(0, len(docs), batch_size):
        chunk = docs[i : i + batch_size]
        task = index.add_documents(chunk)
        print(f"  已提交批次 {i // batch_size + 1}，{len(chunk)} 条，task={task.task_uid}")


def main() -> int:
    parser = argparse.ArgumentParser(description="导入 Phase 1 索引到 Meilisearch")
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="删除并重建索引（清空该 index 下原有文档）",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="每批上传条数（默认 1000）",
    )
    args = parser.parse_args()

    if not JSONL_PATH.is_file():
        print("未找到 Phase 1 索引:", JSONL_PATH, file=sys.stderr)
        print("请先运行: python tools/build_phase1_index.py", file=sys.stderr)
        return 1

    docs = load_documents(JSONL_PATH)
    if not docs:
        print("JSONL 无记录", file=sys.stderr)
        return 1

    client = get_client()
    ensure_index(client, MEILI_INDEX, args.recreate)
    index = client.index(MEILI_INDEX)
    configure_index(index)
    print(f"上传至 Meilisearch index={MEILI_INDEX!r}，共 {len(docs)} 条 …")
    upload_batches(index, docs, args.batch_size)
    print("完成。检索示例：")
    print(f"  python tools/query_meilisearch.py 姑苏")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
