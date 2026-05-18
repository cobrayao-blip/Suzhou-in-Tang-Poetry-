# 全唐诗语料 — Agent 说明

本仓库是《全唐诗》（曹寅、彭定求等）的 **XHTML 正文**（`quantangshi/`）及衍生的 **结构化索引**，供校对、检索与数字人文使用。

## 目录结构

```
项目根/
├── AGENTS.md                 # 本文件
├── quantangshi/
│   └── text00001.html … text00900.html   # 各卷正文（约 900 个）
├── juanmu.xml                # 卷目导航（与 HTML 卷名一致）
├── tools/
│   ├── corpus_paths.py       # 语料路径（可用 QTS_CORPUS / QTS_JUANMU）
│   ├── convert_toc_to_juanmu.py  # 旧 toc.ncx → juanmu.xml（迁移用）
│   ├── build_phase1_index.py # 解析 HTML → 索引
│   ├── normalize_juan_titles.py  # 统一卷名写法
│   ├── normalize_pian_ti_prefix.py  # 补全篇题「卷_N_序号【」
│   ├── build_meilisearch_index.py # JSONL → Meilisearch
│   ├── query_meilisearch.py       # 命令行检索
│   └── sync_postgres.py           # JSONL → PostgreSQL
├── apps/
│   ├── api/                       # FastAPI 检索服务
│   └── web/                       # React 检索前端
├── db/schema.sql                  # PostgreSQL 表结构
├── index/
│   ├── quatangshi_phase1.sqlite
│   └── quatangshi_phase1.jsonl
└── .cursor/
    ├── skills/quatangshi/    # 专项 Skill（@quatangshi）
    └── rules/                # 编辑 HTML/目录时的规则
```

## 你的角色

- 协助 **校对与统一版式**（卷名、篇题、作者标记）
- 维护并 **重建第一期索引**
- **不要** 在无要求时大规模重写正文、不要擅自 `git commit`

更细的流程与字段说明见：`.cursor/skills/quatangshi/SKILL.md`（对话中可 `@quatangshi`）。

**开发说明（审阅用）**：见 [`docs/README.md`](docs/README.md) — 正式编码前的完整设计文档。

## 正文 HTML 语义

| 标记 | 含义 |
|------|------|
| `h1.OneTitle` | 卷名 |
| `p.Bold` | 篇题（可含 `卷19_1【…】`） |
| `p.Quotation` | 作者 |
| `p.Text` | 诗句 |
| `p.PoetryText` | 联句、句编、评注式摘录 |

## 常用命令

在项目根目录执行：

```bash
# 改 HTML / 索引逻辑后（Agent 改完语料应自动跑 rebuild_all，勿每次向用户复述）
python tools/rebuild_all.py

# 仅重建 Phase 1（不碰检索）
python tools/build_phase1_index.py

# 统一误用卷名（卷XXX / 卷XXX卷 → 第XXX卷），并更新 juanmu.xml
python tools/normalize_juan_titles.py

# 补全篇题卷号（卷_1【 → 卷147_1【）
python tools/normalize_pian_ti_prefix.py

# 篇题序号连续性排查（跳号、重复、卷号与文件名不符等）
python tools/validate_pian_ti_sequence.py

# 篇题错位、句编卷清单（可加 --fix-safe 自动修明确错位）
python tools/scan_corpus_structure.py

# 作者行与诗句粘连
python tools/scan_merged_author_quotation.py

# 无作者扫描（体例性缺失 vs 疑似漏标）
python tools/scan_missing_author.py

# 全文检索（需 docker compose up -d 与 requirements-search.txt）
python tools/build_meilisearch_index.py
```

检索服务说明见 `docs/13-Meilisearch检索服务.md`。

## 检索 MVP（PostgreSQL + Web）

```bash
docker compose up -d
pip install -r requirements-dev.txt
python tools/build_phase1_index.py
# PowerShell: $env:MEILI_API_KEY="dev-master-key-change-me"
python tools/build_meilisearch_index.py --recreate
python tools/sync_postgres.py
cd apps/api && uvicorn app.main:app --reload --port 8000
cd apps/web && npm install && npm run dev
```

详见 `docs/14-开发计划-检索MVP-PostgreSQL.md`、`apps/README.md`。

## 版式约定（摘要）

1. **卷名**：`第…卷`；改 `<title>`、`<h1>` 时同步 `juanmu.xml` 对应 `<item>`。
2. **篇题**：`卷{卷号}_{序号}【题名】`；勿与卷名混淆。
3. **索引**：修改语料后运行 `build_phase1_index.py`，产物在 `index/`。

## 第一期索引

- 约 **4.1 万条**记录（含句编等拆条，不等于「诗首」数）
- 字段：卷名、篇题、作者、正文、体裁大类/小类（从 `【】` 解析）
- `parse_note` 标记解析异常，清洗时优先排查

## 语言

与用户沟通使用 **简体中文**。
