# 全唐诗 — 对外入口

## 证书（唯一路径）

`/data/qts/cert/tp.textengine.cn_bundle.crt` 与 `tp.textengine.cn.key` — 见 [证书路径.md](./证书路径.md)。

## 单 IP：tp 不进清嘉录

**不要**使用 `tp.textengine.cn.mount.conf` 挂进清嘉录容器。

按 **[第一步-单IP-tp不进qjl.md](./第一步-单IP-tp不进qjl.md)**：宿主机 Nginx 统一 443。

| 文件 | 用途 |
|------|------|
| `host-nginx-both.conf.example` | 宿主机 `qjl` + `tp` 两个 server |
| `qjl-仅释放443-端口.override.example.yml` | 仅清嘉录 web 改端口，**不含 tp** |
| `tp.textengine.cn.conf` | 仅 tp、且宿主机已占 443 时可用 |

日常：只在 `/opt/quatangshi` `git pull` + `docker compose up -d`。
