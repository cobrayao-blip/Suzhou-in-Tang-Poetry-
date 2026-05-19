# 单 IP：tp 不进清嘉录（推荐方案）

## 不要用：把 tp.conf 挂进清嘉录 web 容器

该做法会让 **清嘉录无法登录**（与 tp 共用同一 Nginx 进程）。请删除这类 override：

```bash
cd /data/qjl/app
sudo mv docker-compose.override.yml docker-compose.override.yml.bak 2>/dev/null || true
sudo docker compose -f docker-compose.prod.yml --env-file .env.docker.prod up -d web
```

确认 `https://qjl.textengine.cn` 能登录后再做下面步骤。

---

## 正确做法：宿主机 Nginx 统一 443

```text
浏览器 → 宿主机 Nginx :443
           ├─ qjl.textengine.cn → 127.0.0.1:18081（清嘉录容器，仅 HTTP）
           └─ tp.textengine.cn   → 127.0.0.1:18080（全唐诗容器）
```

### 1. 全唐诗本机正常

```bash
curl -s http://127.0.0.1:18080/api/health
```

### 2. 清嘉录 web 释放 443（只做端口，不含 tp 配置）

```bash
cd /data/qjl/app
sudo cp /opt/quatangshi/deploy/server/qjl-仅释放443-端口.override.example.yml ./docker-compose.override.yml
sudo docker compose -f docker-compose.prod.yml -f docker-compose.override.yml \
  --env-file .env.docker.prod up -d web
curl -s http://127.0.0.1:18081/ | head -3
```

### 3. 安装宿主机 Nginx

```bash
sudo apt-get install -y nginx
sudo cp /opt/quatangshi/deploy/server/host-nginx-both.conf.example /etc/nginx/sites-available/textengine.conf
sudo ln -sf /etc/nginx/sites-available/textengine.conf /etc/nginx/sites-enabled/textengine.conf
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```

证书路径见 `证书路径.md`（tp 在 `/data/qts/cert/`）。

### 4. 验收

```bash
curl -s https://tp.textengine.cn/api/health
curl -sI https://qjl.textengine.cn | head -3
```

浏览器分别登录清嘉录、打开全唐诗。
