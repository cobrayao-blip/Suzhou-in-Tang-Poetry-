# 服务器边缘反代（与业务代码分离）

本目录 **只属于全唐诗项目**，文件名不含其他产品名称。  
全唐诗 Docker 只监听 **`127.0.0.1:18080`**，不占用公网 443。

## 两个域名是做什么的？

| 域名 | 产品 | 本仓库 |
|------|------|--------|
| `qjl.textengine.cn` | 清嘉录 | 无关 |
| `tp.textengine.cn` | 全唐诗检索 | 本应用 |

域名分开 = **对外两个入口**，不是要把两个项目代码绑在一起。

## 本机结构（正确理解）

```text
浏览器 → tp.textengine.cn (443) → 【边缘反代，服务器上配置一次】→ 127.0.0.1:18080 → 全唐诗容器
浏览器 → qjl.textengine.cn (443) → 【另一套反代/容器】→ 清嘉录
```

「边缘反代」可以在：

1. **宿主机 Nginx/Caddy**（推荐，见 `edge-nginx.example.conf`）  
2. 或当前已占用 443 的那个 Nginx 容器里 **include 本目录的 `tp.textengine.cn.conf`**（由服务器管理员操作，**不要写进本 Git 仓库以外的项目源码**）

## SSL（仅 tp 域名）

证书与私钥建议目录（与清嘉录分开）：

```text
/data/certs/tp.textengine.cn/fullchain.pem
/data/certs/tp.textengine.cn/privkey.pem
```

若有 `*.textengine.cn` 通配符，可复用同一套 PEM，并在 `tp.textengine.cn.conf` 里改路径。

签发示例：

```bash
sudo certbot certonly --nginx -d tp.textengine.cn
# 或 DNS 验证；证书拷到 /data/certs/tp.textengine.cn/
```

## 安装 tp 反代片段

```bash
sudo mkdir -p /data/certs/tp.textengine.cn
sudo cp /opt/quatangshi/deploy/server/tp.textengine.cn.conf /data/nginx-sites/tp.textengine.cn.conf
# 由管理员 include 到实际监听 443 的 Nginx，或改用 edge-nginx.example.conf
```

`tp.textengine.cn.conf` 内 upstream 为 `127.0.0.1:18080`（不依赖 Docker 特殊主机名）。

## 日常更新全唐诗

与边缘反代无关，只需：

```bash
cd /opt/quatangshi && git pull
# 见 ../部署手册.md 第十三节
```
