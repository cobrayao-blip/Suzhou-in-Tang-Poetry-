---
name: quatangshi
description: >-
  Maintains the Quan Tang Shi XHTML corpus (quantangshi/), phase-1 poem index
  (SQLite/JSONL), and normalization scripts. Use when editing 全唐诗 HTML,
  rebuilding index, fixing 卷名/篇题/体裁, or working in this repository's
  quantangshi, tools, or index folders.
---

# 全唐诗语料工程

## 项目根

以包含 `quantangshi/`、`tools/`、`index/` 的目录为 **ROOT**。

## 目录

| 路径 | 说明 |
|------|------|
| `quantangshi/text*.html` | 约 900 卷正文 XHTML |
| `juanmu.xml`（项目根） | 卷目导航，卷名须与 HTML 一致 |
| `tools/corpus_paths.py` | 语料路径；可用 `QTS_CORPUS`、`QTS_JUANMU` 覆盖 |
| `tools/build_phase1_index.py` | 生成第一期索引 |
| `tools/normalize_juan_titles.py` | 统一误用卷名 |
| `index/quatangshi_phase1.sqlite` | 索引库 |
| `index/quatangshi_phase1.jsonl` | 索引行（JSON Lines） |

## HTML 结构（解析约定）

每卷 `textNNNNN.html`：

- `<title>` / `<h1 class="OneTitle">`：**卷名**（`juan_ming`）
- `<p class="Bold">`：**篇题**（常含 `卷19_5【相和歌辞·公无渡河】`）
- `<p class="Quotation">`：**作者**；少数卷作者写在第二个 `Bold`
- `<p class="Text">`：**诗句行**
- `<p class="PoetryText">`：联句、句编、格话等（无标准篇题时按行收录）

篇题识别：以 `卷\d+_\d+【` 或 `\d+_\d+【` 开头；连续多个 `Bold` 在未闭合 `【…】` 时合并为一篇题。

体裁：篇题第一个 `【…】` 内，按第一个 `·` 拆为 `ticai_da` / `ticai_xiao`。

## 卷名规范

- **标准**：`第` + 中文数词 + 尾 `卷`（如 `第六百七十一卷`、`第十九卷`）
- **勿用**：`卷六百五十八卷`、`卷八百三十`（缺尾卷）
- 改卷名须同步：`<title>`、`<h1 class="OneTitle">`、`juanmu.xml` 中对应 `<item>`
- 篇题里的 `卷658_1` 是**卷内序号**，不是卷名，不要改成 `第…卷`

## 篇题规范

- 统一为 `卷{N}_{序号}【…】`（缺 `卷` 前缀的需补上，与同文件相邻篇题一致）
- `【` 前空格：与同卷其它篇题保持一致（如 `卷708_16 【香鸭】`）

## 工作流

### 修改正文或元数据后

```bash
python tools/build_phase1_index.py
python tools/sync_postgres.py
python tools/build_meilisearch_index.py --recreate
```

（Agent 改完语料后应自动执行上述三条，无需每次提醒用户。）

### 批量修正误用卷名（或从外部拷回旧文件后）

```bash
python tools/normalize_juan_titles.py
python tools/build_phase1_index.py
```

### 批量补全篇题卷号（`卷_1【` → `卷147_1【`）

```bash
python tools/normalize_pian_ti_prefix.py
python tools/build_phase1_index.py
```

### 小范围手工改 HTML

1. 只改相关 `text*.html`，避免无关卷
2. 若动卷名 → 同步 `juanmu.xml`
3. 重建索引

## 索引字段（`poems` 表 / JSONL）

`id`, `source_file`, `juan_ming`, `pian_ti`, `zuo_zhe`, `zheng_wen`, `ticai_da`, `ticai_xiao`, `kuohao_nei`, `parse_note`

- `parse_note` 非空：杂录、缺作者/正文等，清洗时优先看；`author_inferred_from_volume` 为卷内继承，非结构错误
- 构建索引时自动**卷内作者继承**（歌辞/句编卷除外）
- 无作者报告：`python tools/scan_missing_author.py` → `index/missing_author_report.json`
- 勿在未确认前删除带 `PoetryText` 的整卷

## 已知边缘情况

- 多行 `Bold` 篇题（标题在第二段 `Bold`）
- 空 `<p class="Bold"></p>` 分隔（如 text00649）
- 无 `Quotation`、仅 `PoetryText` 的句编卷（如 text00795）
- 缺 `】` 的篇题 → 体裁字段可能为空

## 全文检索（Meilisearch）

```bash
docker compose up -d
pip install -r requirements-search.txt
python tools/build_phase1_index.py
python tools/build_meilisearch_index.py
python tools/query_meilisearch.py 关键词
```

详见 `docs/13-Meilisearch检索服务.md`。

## 第二期（未实现，勿承诺）

诗首展开、苏州子集、意象词表、诗人年表等——见 `docs/` 路线图。

## 原则

- 小步 diff，不批量「顺手」改格式
- 不提交除非用户明确要求
- 回复用户用简体中文
