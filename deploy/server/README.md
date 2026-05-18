# 全唐诗 — 对外入口

## 证书放哪里？（唯一答案）

**`/data/qts/cert/tp.textengine.cn_bundle.crt`** 与 **`tp.textengine.cn.key`**  
详见 **[证书路径.md](./证书路径.md)**。不要用 `/data/certs/...`。

## 你现在要做的事（单 IP，tp 不进 qjl）

按 **[第一步-单IP-tp不进qjl.md](./第一步-单IP-tp不进qjl.md)** 做即可。

用到的文件：

| 文件 | 用途 |
|------|------|
| `tp.textengine.cn.mount.conf` | 复制到 `/data/nginx-extra/tp.textengine.cn.conf` |
| `docker-compose.override.example.yml` | 复制到占 443 的 web 目录为 `docker-compose.override.yml` |
| 证书 | `/data/qts/cert/tp.textengine.cn_bundle.crt` 与 `.key` |

全唐诗应用端口：`127.0.0.1:18080`。

## 其它（以后再说）

| 文件 | 何时用 |
|------|--------|
| `tp.textengine.cn.conf` | 宿主机 Nginx 接管 443 时 |
| `tp.textengine.cn.edge.conf` + compose `--profile edge` | 为 tp 单独公网 IP 时 |

日常只在 `/opt/quatangshi`：`git pull` + `docker compose up -d --build`。
