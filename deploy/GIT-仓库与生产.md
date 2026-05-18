# Git 仓库与生产环境：哪些进 GitHub、服务器 pull 后做什么

生产更新流程：**开发机改代码 → `git push` → 服务器与 GitHub 对齐 → 重建索引与 Docker**。

操作步骤见本机 **`deploy/部署手册.md`**（该文件 **不入 GitHub**，服务器上不会有）。

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
| 设计文档 | `docs/` | 仅本机 |
| 部署手册 | `deploy/部署手册.md` | **仅本机**；服务器不需要 |
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
| `deploy/`（除部署手册外） | Compose、`Dockerfile.prod`、`requirements.api.prod.txt`、`nginx.docker.conf`、`server/tp.textengine.cn.conf` |
| `db/schema.sql` | 数据库表结构 |
| `deploy/requirements.api.prod.txt` | Docker 构建时 Python 依赖 |
| `.env.example`、`deploy/.env.prod.example` | 环境变量模板 |

---

## 三、服务器 `git pull` 是在拉什么？

**不是**拉部署手册。服务器只需要能 **构建和运行** 的文件，例如：

- 语料 `quantangshi/`、应用 `apps/`、索引脚本 `tools/build_*.py`
- `deploy/Dockerfile.prod`、`deploy/docker-compose.prod.yml`、`deploy/.env.prod`（本地创建）

**不要在服务器上手改** `deploy/` 等仓库文件；改本机 → `git push` → 服务器用下面命令 **与 GitHub 完全一致**。

## 四、服务器标准更新命令

```bash
cd /opt/quatangshi
git fetch origin main
git reset --hard origin/main
python3 tools/build_phase1_index.py
sudo docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env.prod up -d --build
sudo docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env.prod --profile bootstrap run --rm bootstrap
```

`reset --hard` 会丢弃服务器上对仓库的手改（**保留** `deploy/.env.prod` 若已加入 `.gitignore`）。仅改前端、未改语料时，可省略索引与 `bootstrap`。

---

## 五、开发机说明

语料校对脚本（`scan_*`、`normalize_*` 等）**只留在你的 Windows 开发机**，不提交 GitHub。换电脑时需自行备份 `tools/` 下这些文件，或从旧提交/同事处拷贝。

设计文档 `docs/` 同样只保留在开发机；团队共享可另建文档仓库或使用 GitHub Wiki。
