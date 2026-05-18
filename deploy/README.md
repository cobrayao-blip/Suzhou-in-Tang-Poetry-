# 全唐诗检索 — 生产部署

> **零基础请直接阅读：[部署手册.md](./部署手册.md)**（逐步复制命令即可）。  
> **Git 与生产分工**：[GIT-仓库与生产.md](./GIT-仓库与生产.md)。  
> 本文档供已熟悉 Linux/Docker 的维护者速查。

正式域名：**`https://tp.textengine.cn`**（与清嘉录 `qjl.textengine.cn` 平级，独立子域）。

## 腾讯云（与清嘉录同机）

| 项 | 值 |
|----|-----|
| 公网 IP | **43.142.176.9**（DNS A 记录指向此地址，勿填内网 172.17.0.7） |
| 内网 IP | 172.17.0.7（VPC `172.17.0.0/16`） |
| 系统 | Ubuntu Server 24.04 LTS，2 核 / 4GiB |
| 磁盘 | 系统盘 60GiB + 数据盘 60GiB（库与索引建议放数据盘 `/data/qts/`） |
| Docker | 29.x（`docker compose`） |
| 清嘉录 | 同机 `qjl.textengine.cn`，见 `/data/qjl/app` |

4GiB 内存可同时跑 PostgreSQL + Meilisearch + API；首次 `bootstrap` 导入时 CPU/磁盘会忙一阵，属正常。

## 1. DNS

在 `textengine.cn` 控制台为 **`tp`** 添加 **A 记录** → **`43.142.176.9`**。

## 2. 与清嘉录共存

清嘉录已占用 **80/443**。全唐诗栈默认只监听 **`127.0.0.1:18080`**，由**宿主机 Nginx** 按 `server_name tp.textengine.cn` 转发（见 `nginx-host-tp.conf`）。

若清嘉录容器内 Nginx 为 `server_name _`，需在宿主机增加 `tp.textengine.cn` 的 `server` 块，或把清嘉录改为仅 `qjl.textengine.cn`。

**HTTPS**：`qjl.textengine.cn` 证书不能用于 `tp.textengine.cn`，需单独签发或使用 `*.textengine.cn` 通配符：

```bash
certbot certonly --nginx -d tp.textengine.cn
```

签发后确认 `deploy/nginx-host-tp.conf` 中 `ssl_certificate` 路径与实机一致。

## 3. 服务器目录

```bash
mkdir -p /opt/quatangshi /data/qts/pgdata /data/qts/meili
```

本机打包上传：

```powershell
python tools/build_phase1_index.py
.\deploy\pack-for-server.ps1
scp dist-quatangshi-deploy.zip ubuntu@43.142.176.9:/tmp/
# 登录服务器后：sudo mv /tmp/dist-quatangshi-deploy.zip /opt/quatangshi/ && cd /opt/quatangshi && sudo unzip -o dist-quatangshi-deploy.zip
```

```bash
cd /opt/quatangshi && unzip -o dist-quatangshi-deploy.zip
cp deploy/.env.prod.example deploy/.env.prod
# 编辑 deploy/.env.prod：POSTGRES_PASSWORD、MEILI_MASTER_KEY
```

## 4. 启动

```bash
cd /opt/quatangshi
docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env.prod up -d --build

docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env.prod --profile bootstrap run --rm bootstrap
```

验证：

```bash
curl -s http://127.0.0.1:18080/api/health
```

## 5. 宿主机 Nginx

```bash
cp deploy/nginx-host-tp.conf /etc/nginx/conf.d/tp.textengine.cn.conf
nginx -t && systemctl reload nginx
```

浏览器打开：**https://tp.textengine.cn**

## 6. 更新索引

```bash
docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env.prod up -d --build api web
docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env.prod --profile bootstrap run --rm bootstrap
```
