# Git 仓库与生产环境：哪些进 GitHub、服务器 pull 后做什么

生产更新流程：**开发机改代码 → `git push` → 服务器 `git pull` → 重建索引与 Docker**（见 [部署手册.md](./部署手册.md) 第十三节）。

---

## 一、不进 GitHub（`.gitignore` 已排除）

| 类别 | 路径 | 原因 |
|------|------|------|
| 密钥 | `.env`、`deploy/.env.prod` | 仅服务器本地配置 |
| 生成索引 | `index/*.jsonl`、`*.sqlite`、`*_report.json` | `build_phase1_index.py` 在服务器生成 |
| 依赖构建 | `node_modules/`、`apps/web/dist/` | Docker 构建时生成 |
| IDE | `.cursor/`、`AGENTS.md` | 仅 Cursor 开发 |
| 备忘 | `问题汇总备忘.md` | 个人笔记 |
| 废弃代码 | `tang-verse-explorer/` | 旧原型 |
| 设计文档 | `docs/` | 生产不读；开发在 GitHub 网页看（**已从仓库移除**，本地 `docs/` 仍保留） |
| 本地开发 | `docker-compose.yml`、`requirements-dev.txt` | 生产用 `deploy/docker-compose.prod.yml` |
| 旧部署方式 | `pack-for-server.ps1`、`qingjialu-*.conf` 等 | 已删除；反代见 `deploy/server/` |
| 语料校对脚本 | `tools/scan_*`、`normalize_*`、`validate_*` 等 | 仅开发机改 HTML；**不进 GitHub** |

---

## 二、必须在 GitHub（服务器 `git pull` 需要）

| 路径 | 用途 |
|------|------|
| `quantangshi/` | 语料源；服务器生成 Phase 1 索引 |
| `juanmu.xml` | 卷目，与语料一致 |
| `tools/build_phase1_index.py` | 生成 `index/quatangshi_phase1.jsonl` |
| `tools/build_meilisearch_index.py` | bootstrap 导入 Meilisearch |
| `tools/sync_postgres.py` | bootstrap 导入 PostgreSQL |
| `tools/corpus_paths.py` | 上述脚本依赖 |
| `apps/api/`、`apps/web/` | Docker 构建前后端 |
| `deploy/` | Compose、Dockerfile、容器内 `nginx.docker.conf`、`部署手册.md`、`server/tp.textengine.cn.conf` |
| `db/schema.sql` | 数据库表结构 |
| `deploy/requirements.api.prod.txt` | Docker 构建时 Python 依赖 |
| `.env.example`、`deploy/.env.prod.example` | 环境变量模板 |

---

## 三、服务器标准更新命令

```bash
cd /opt/quatangshi
git pull
python3 tools/build_phase1_index.py
sudo docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env.prod up -d --build
sudo docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env.prod --profile bootstrap run --rm bootstrap
```

仅改前端文案、未改语料时，可省略 `build_phase1_index.py` 与 `bootstrap`（只 `up -d --build`）。

---

## 四、开发机说明

语料校对脚本（`scan_*`、`normalize_*` 等）**只留在你的 Windows 开发机**，不提交 GitHub。换电脑时需自行备份 `tools/` 下这些文件，或从旧提交/同事处拷贝。

设计文档 `docs/` 同样只保留在开发机；团队共享可另建文档仓库或使用 GitHub Wiki。
