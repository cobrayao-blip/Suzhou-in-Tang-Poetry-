# 全唐诗 — 宿主机 Nginx 与证书

## 证书（唯一路径）

`/data/qts/cert/tp.textengine.cn_bundle.crt` 与 `tp.textengine.cn.key` — 见 [证书路径.md](./证书路径.md)。

## 生产推荐（与清嘉录解耦）

```text
宿主机 Nginx :443
  qjl.textengine.cn → 127.0.0.1:18081   （清嘉录，站点文件由清嘉录侧维护）
  tp.textengine.cn   → 127.0.0.1:18080   （全唐诗，见下）
```

| 文件 | 用途 |
|------|------|
| `tp.textengine.cn.conf` | 复制为 `/etc/nginx/sites-available/tp.textengine.cn` |
| `host-nginx-both.conf.example` | 参考：qjl + tp 合在一文件的写法 |
| `qjl-仅释放443-端口.override.example.yml` | 清嘉录目录一次性端口映射（**不含 tp**） |

**勿用** `tp.textengine.cn.mount.conf`（挂进清嘉录容器会导致清嘉录无法登录）。

操作步骤见 **`deploy/部署手册.md` 第十一节**。

## 可选：tp 单独公网 IP

使用 `deploy/docker-compose.edge.yml` 与 `QTS_PUBLIC_IP`（见 `.env.prod.example` 注释），与「宿主机 Nginx 分流」二选一。

## 日常

仅在 `/opt/quatangshi`：`git pull` + `docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env.prod up -d --build`。
