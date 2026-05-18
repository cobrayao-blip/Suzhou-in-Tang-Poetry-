# 全唐诗检索应用

## 快速启动

```bash
# 项目根目录
cp .env.example .env
docker compose up -d

pip install -r requirements-dev.txt
python tools/build_phase1_index.py
python tools/build_meilisearch_index.py --recreate
python tools/sync_postgres.py

# 终端 1 — API
cd apps/api
uvicorn app.main:app --reload --port 8000

# 终端 2 — 前端
cd apps/web
npm install
npm run dev
```

- 前端：http://127.0.0.1:5173  
- API 文档：http://127.0.0.1:8000/docs  

生产部署（`https://tp.textengine.cn`）：见 [`deploy/README.md`](../deploy/README.md)。
