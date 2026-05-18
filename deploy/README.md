# 全唐诗检索 — 生产部署

正式域名：**`https://tp.textengine.cn`**（与清嘉录 `qjl.textengine.cn` 平级，独立子域）。

## 1. DNS

在 `textengine.cn` 控制台为 **`tp`** 添加 **A 记录** → 服务器公网 IP（与清嘉录可同机）。

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
scp dist-quatangshi-deploy.zip root@<服务器IP>:/opt/quatangshi/
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
