# 13 — Meilisearch 自建检索

Phase 2b 的**全文检索**采用 [Meilisearch](https://www.meilisearch.com/) 自建服务，不用 SQLite FTS5。Phase 1 的 SQLite/JSONL 仍为结构化查询与重建源；Meilisearch 为**可重建的检索副本**。

## 13.1 架构位置

```
quantangshi/*.html
    → build_phase1_index.py → index/quatangshi_phase1.jsonl
    → build_meilisearch_index.py → Meilisearch 索引 quatangshi
```

- **不**改写 HTML。
- Meilisearch 数据丢失时，可从 JSONL 全量重导。

## 13.2 本地运行

### 启动服务

```bash
# 项目根目录
docker compose up -d
```

默认：

| 项 | 值 |
|----|-----|
| 地址 | http://127.0.0.1:7700 |
| Master Key | `dev-master-key-change-me`（见 `docker-compose.yml`，生产务必修改） |

### 安装 Python 依赖（仅检索相关）

```bash
pip install -r requirements-search.txt
```

### 导入索引

```bash
python tools/build_phase1_index.py
set MEILI_API_KEY=dev-master-key-change-me
python tools/build_meilisearch_index.py
# 重建索引（清空后重导）：
python tools/build_meilisearch_index.py --recreate
```

### 查询示例

```bash
python tools/query_meilisearch.py 姑苏
python tools/query_meilisearch.py 刘长卿 --filter "zuo_zhe = \"刘长卿\"" -n 5
```

## 13.3 环境变量

| 变量 | 默认 | 说明 |
|------|------|------|
| `MEILI_HOST` | `http://127.0.0.1:7700` | 服务地址 |
| `MEILI_API_KEY` | 空 | 与 `MEILI_MASTER_KEY` 一致；开发 Docker 默认见 compose |
| `MEILI_INDEX` | `quatangshi` | 索引 UID |

## 13.4 索引字段设计

| 类型 | 字段 |
|------|------|
| **主键** | `id` |
| **可搜索** | `zheng_wen`, `pian_ti`, `zuo_zhe`, `juan_ming`, `ticai_da`, `ticai_xiao`, `kuohao_nei` |
| **可筛选** | `zuo_zhe`, `juan_ming`, `source_file`, `ticai_da`, `ticai_xiao`, `parse_note` |
| **展示** | 上表全部 |

组诗多条仍对应一条文档（与 Phase 1 一致）；诗首级检索待 Phase 2a 另建索引或同索引加 `parent_id` 字段。

## 13.5 运维约定

1. 改 HTML 后：`build_phase1_index.py` → `build_meilisearch_index.py`（或 `--recreate`）。
2. 生产环境：独立主机/容器、强 Master Key、数据卷备份 `meili_data`。
3. 不把 Meilisearch 数据目录提交 Git；只提交构建脚本与 compose。

## 13.6 与苏州子集的关系

- 苏州子集仍可在 JSONL 层用 `build_suzhou_index.py`（规划）生成 `suzhou_phase1.jsonl`。
- 可选：第二索引 `MEILI_INDEX=suzhou` 仅导入子集；或在 `quatangshi` 索引上用 `filter` + 关键词组合查询。

## 13.7 验收（对应文档 10）

- [ ] `docker compose up -d` 后 7700 可访问
- [ ] `build_meilisearch_index.py` 导入 41 375 条无报错
- [ ] `query_meilisearch.py 姑苏` 命中含「姑苏」相关名篇
- [ ] `query_meilisearch.py 刘长卿 --filter ...` 仅返回该作者
