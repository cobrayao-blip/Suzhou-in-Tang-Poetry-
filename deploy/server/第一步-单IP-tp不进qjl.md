# 第一步：单 IP，让 tp.textengine.cn 不再打开清嘉录

**前提**：全唐诗 Docker 已正常。

```bash
curl -s http://127.0.0.1:18080/api/health
# 必须是 {"status":"ok"}
```

**原理**：本机只有一台 Nginx 占着 `443`。它原来用 `server_name _` 会吃掉所有域名。  
再加一个 **`server_name tp.textengine.cn`** 的 server 块后，访问 `tp` 会优先走全唐诗，**不用改清嘉录业务代码**。

全唐诗只提供 `/data/nginx-extra/` 里的片段；清嘉录仓库里的 `nginx.docker.conf` **不用动**。

---

## A. 准备 tp 证书（全唐诗目录）

```bash
sudo mkdir -p /data/qts/cert /data/nginx-extra
```

把 `tp.textengine.cn` 的证书放到（文件名固定）：

- `/data/qts/cert/tp.textengine.cn_bundle.crt`
- `/data/qts/cert/tp.textengine.cn.key`

有 `*.textengine.cn` 通配符时，内容正确即可，复制并重命名为上面两个文件。

```bash
sudo cp /opt/quatangshi/deploy/server/tp.textengine.cn.mount.conf /data/nginx-extra/tp.textengine.cn.conf
```

---

## B. 挂进当前占 443 的 web 容器（一次性）

清嘉录 web 容器路径以你机器为准，常见 `/data/qjl/app`：

```bash
cd /data/qjl/app
sudo cp /opt/quatangshi/deploy/server/docker-compose.override.example.yml ./docker-compose.override.yml
sudo docker compose -f docker-compose.prod.yml -f docker-compose.override.yml \
  --env-file .env.docker.prod up -d web
```

---

## C. 验收

```bash
curl -s https://tp.textengine.cn/api/health
```

应为 `{"status":"ok"}`。浏览器应是「全唐诗 · 检索」，不是清嘉录登录。

```bash
curl -sI https://qjl.textengine.cn | head -3
```

清嘉录仍应正常（未改其 `server_name _` 块，只多了 tp 专用块）。

---

## 以后更新

| 项目 | 做法 |
|------|------|
| 全唐诗 | `cd /opt/quatangshi` → `git pull` → `docker compose ... up -d --build` |
| 清嘉录 | 在清嘉录目录 `git pull`；**保留** `docker-compose.override.yml` |

若清嘉录 `up -d web` 后 tp 又不对，检查 override 是否还在：`cat docker-compose.override.yml`
