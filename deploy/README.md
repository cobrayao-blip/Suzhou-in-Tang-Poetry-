# 全唐诗 — 生产部署

| 文档 | 读者 |
|------|------|
| [部署手册.md](./部署手册.md) | 从零部署 |
| [GIT-仓库与生产.md](./GIT-仓库与生产.md) | 什么进 GitHub、服务器 `git pull` |
| [server/README.md](./server/README.md) | 域名 / SSL / 边缘反代（与业务仓库分离） |

域名：**https://tp.textengine.cn** · 服务器：`ubuntu@43.142.176.9` · 代码目录：`/opt/quatangshi`

日常更新：`git push`（本机）→ `git pull` + Docker（服务器），见部署手册第十三节。
