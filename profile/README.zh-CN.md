<div align="center">

[한국어](README.md) · [English](README.en.md) · [日本語](README.ja.md) · **简体中文**

# nginx manager

**别再因为手改配置文件把站点弄挂了。在浏览器里确认、应用，失败时自动回滚。**

用两个容器运行 nginx 和管理界面的 Web 版 nginx 管理工具

[![Release](https://img.shields.io/badge/release-v1.9.1-10b981.svg)](https://github.com/nginx-manager/app/releases/tag/v1.9.1)
[![nginx](https://img.shields.io/badge/nginx-1.31.8-009639.svg)](https://nginx.org/en/CHANGES)
[![Languages](https://img.shields.io/badge/UI-%ED%95%9C%EA%B5%AD%EC%96%B4%20%C2%B7%20English%20%C2%B7%20%E6%97%A5%E6%9C%AC%E8%AA%9E%20%C2%B7%20%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87-0ea5e9.svg)](#四种语言和深色模式)

[在服务器上安装](#在服务器上安装) · [主要功能](#主要功能) · [发行说明](https://github.com/nginx-manager/app/blob/main/docs/releases/README.md) · [仓库](https://github.com/nginx-manager/app)

</div>

<p align="center">
  <img src="images/dashboard.png" alt="nginx manager 仪表盘" width="860" />
</p>

## 目录

- [为什么选择 nginx manager](#为什么选择-nginx-manager)
- [在服务器上安装](#在服务器上安装)
- [主要功能](#主要功能)
- [架构](#架构)
- [仓库](#仓库)
- [发行版本](#发行版本)

## 为什么选择 nginx manager

| | 在服务器上直接修改 | nginx manager |
| --- | --- | --- |
| 添加站点 | 手写配置文件 | 用**表单**创建反向代理、静态站点和 TCP/UDP 流，并即时预览生成的配置 |
| 生效 | `nginx -t` 后 reload，失败时手动恢复 | **查看 diff → 校验 → reload → 检查状态**，任一步失败都会**自动恢复上一份配置** |
| 历史 | 自己管理备份文件 | 每次应用都会留下**版本**，可比较、可回滚，并能发现在服务器上被直接修改的文件 |
| HTTPS | 安装 certbot 并安排续期 | 为站点选择 HTTPS 后，**Let's Encrypt 签发、配置和续期**全部自动完成 |
| 日志 | 登录服务器 `tail` | 在**界面上搜索、实时查看**每个站点的 access/error 日志 |
| 权限 | 共用服务器账号 | 管理员和成员两种角色，成员**只管理自己负责的站点**，**所有变更都记入审计日志**，登录可开启**两步验证（TOTP）** |

## 在服务器上安装

需要：Docker Engine 和 Compose v2、sudo 权限、空闲的 80 和 443 端口。若使用管理域名，该域名的 DNS 必须指向这台服务器，且 80 端口能从互联网访问。

下面一行命令会安装到 `/opt/nginx-manager` 并立即启动。

```bash
curl -fsSL https://github.com/nginx-manager/app/releases/latest/download/install.sh \
  | sudo sh -s -- --admin-domain nm.example.com --email ops@example.com
```

- 指定 `--admin-domain` 后，管理界面通过该域名提供：自动申请 Let's Encrypt 证书，80 跳转到 443，管理界面只走 HTTPS。
- 不指定域名时，管理界面只监听服务器上的 `http://127.0.0.1:9000`。在自己的电脑上用 `ssh -L 9000:127.0.0.1:9000 <服务器>` 连接后打开 `http://localhost:9000`。
- 首次访问时会进入创建第一个管理员账号的页面。
- 要导入服务器上已有的 `/home/*/nginx` 配置，安装时加上 `--import-root /home`。安装后可用 `./nm import-root add /home` 添加。
- 其他选项：`--version X.Y.Z`（固定版本）、`--dir`（安装位置）、`--http-port`、`--https-port`、`--manager-port`、`--bundle FILE`（无法联网的服务器）。

### 配置 (`/opt/nginx-manager/.env`)

安装后会生成 `/opt/nginx-manager/.env`。修改后运行 `./nm restart` 重新启动；如果改了 nginx 端口，运行 `./nm restart nginx`。

| 变量 | 默认值 | 何时修改 |
| --- | --- | --- |
| `MANAGER_VERSION`, `NGINX_IMAGE` | 安装的版本 | 不要手动修改，由 `nm upgrade` 更新 |
| `NGINX_MANAGER_ADMIN_DOMAIN` | 空 | 想用 `https://域名` 打开管理界面时 |
| `NGINX_MANAGER_ADMIN_EMAIL` | 空 | Let's Encrypt 联系邮箱 |
| `NGINX_MANAGER_ADMIN_ALLOW` | 空（全部允许） | 用 CIDR 限制可访问管理域名的地址时 |
| `NGINX_MANAGER_PORT` | `9000` | 9000 端口已被占用时 |
| `NGINX_MANAGER_BIND_ADDRESS` | `127.0.0.1` | 不用域名、在内网开放管理界面时（`0.0.0.0` 或内网 IP） |
| `NGINX_HTTP_PORT`, `NGINX_HTTPS_PORT` | `80`, `443` | 前面已有代理占用 80/443 时 |
| `NGINX_BIND_ADDRESS` | `0.0.0.0` | 只让 nginx 监听某个 IP 时 |
| `NGINX_MANAGER_BACKUP_KEEP` | `14` | `nm backup` 保留的份数 |
| `NGINX_MANAGER_BACKUP_AT` | `03:30` | 每日自动备份的时间。设为 `off` 则关闭。修改后运行 `sudo ./nm backup-schedule` |
| `TZ` | `Asia/Seoul` | 时区 |
| `NGINX_MANAGER_IMPORT_ROOTS` | 空 | 导入 `/etc/nginx` 之外的配置文件时 |
| `SPRING_MAIL_*` | 空 | 邮件通知使用的 SMTP 服务器 |

### 运维命令

```bash
cd /opt/nginx-manager
./nm status            # 状态和版本
./nm restart           # 修改 .env 后重新启动
./nm upgrade           # 只升级管理界面（nginx 继续处理流量）
./nm upgrade --nginx   # 同时升级 nginx（先用新 nginx 校验配置，几秒内重启）
./nm backup            # 备份配置和数据库（每天 03:30 也会自动运行）
./nm backup-schedule   # 按 .env 重新安装自动备份计划
./nm reset-2fa <用户>  # 为丢失手机的管理员关闭两步验证
./nm restore backups/<文件>
./nm migrate           # 从 v1.0/v1.1 迁移（先用 --no-start 安装）
./nm import-root check # 检查导入目录是否可读（不可读时用 grant 授予读权限）
```

详见[用户手册第 1 章 安装与运行](https://github.com/nginx-manager/app/blob/main/src/main/resources/guide/ko/01-install.md)（韩语）。

## 主要功能

### 用表单创建站点

多个后端（负载均衡）、WebSocket、超时、重定向乃至 HTTP/3 都能在表单里设置，旁边即时显示生成的 nginx 配置。PHP（PHP-FPM）站点和 gRPC 代理（`grpc://`）也能用表单创建，还可以在站点前放置 oauth2-proxy、Authelia 等外部认证服务器（auth_request）（v1.4.0）。把 `/api/` 发往后端、`/files/` 指向目录的按路径路由，以及备用上游、故障判定和 keepalive 也能在表单中设置（v1.5.0）。CORS、CSP 等响应头、发往后端的头部以及 `www` 到主域名的 301 也能在表单中设置，相似的站点可用**复制**沿用设置，只需填写新域名（v1.6.0）。表单覆盖不到的配置，可在带 nginx 语法高亮的 Raw 编辑器中修改。不再使用的站点可以删除，删除同样经过待应用 → 应用。

<p align="center"><img src="images/site-form.png" alt="添加站点表单与配置预览" width="860" /></p>

### 导入已有配置文件

登记 `/home/*/nginx/*.conf` 这样的路径模式后，会找出所有匹配的文件并一次性登记为站点。能转成表单的成为表单站点，其余登记为 Raw 站点；原文件变化时会提醒你。

<p align="center"><img src="images/import-scan.png" alt="导入配置文件" width="860" /></p>

### TCP/UDP 流

数据库、MQTT 等非 HTTP 服务也能按端口转发。

<p align="center"><img src="images/stream-form.png" alt="添加流表单" width="860" /></p>

### 先确认再应用

保存的变更进入待应用状态，先按文件查看 diff 再生效。`nginx -t`、reload、健康检查中任一步失败，都会自动回滚到上一份配置。

<p align="center"><img src="images/apply-diff.png" alt="应用前的变更内容" width="860" /></p>

### 历史与回滚

每次应用都会留下版本，可以比较任意两个版本或回滚到之前的版本。在站点页面可以只查看改动过该站点的版本，成员也能查看自己负责站点的历史。相同内容只保存一次，版本增多时数据库也不会明显变大（v1.3.0）。

<p align="center"><img src="images/version-diff.png" alt="比较两个版本" width="860" /></p>

### HTTPS 证书

自动申请 Let's Encrypt 证书并在到期前续期。续期失败时通过邮件或 Webhook 通知。通配符证书和内部证书可以上传。通过导入配置文件加入的 Raw 站点也能签发证书，并以待应用形式加入 443 server 块和 80→443 重定向。

<p align="center"><img src="images/certs.png" alt="证书列表" width="860" /></p>

### 日志

搜索或实时查看每个站点的 access/error 日志。也能读取导入的 Raw 站点的日志和轮转后的历史日志。

<p align="center"><img src="images/logs.png" alt="查看站点日志" width="860" /></p>

### 维护模式

部署或数据库作业期间，开启维护模式并应用后，访问者会看到 503 提示页，只有维护人员的地址照常放行。证书签发路径不受影响（v1.5.0）。

### 登录保护与自动备份

在账户页面开启认证器应用（TOTP）两步验证后，输入密码后还需输入 6 位验证码。手机丢失时，可用恢复码、由管理员解除，或在服务器上运行 `nm reset-2fa`。服务器每天自动备份，仪表盘会显示最近一次备份和失败情况（v1.4.0）。

### 四种语言和深色模式

界面可用韩语、英语、日语、简体中文显示，并可切换到深色主题。

<p align="center"><img src="images/sites-en.png" alt="英文界面的站点列表" width="860" /></p>

## 架构

| 容器 | 镜像 | 作用 |
| --- | --- | --- |
| `nginx` | `ghcr.io/nginx-manager/nginx` | nginx（开源版，编译了全部模块）和代理程序。代理程序只按管理界面的请求执行 `nginx -t` 和 reload |
| `manager` | `ghcr.io/nginx-manager/app` | 管理界面（Spring Boot）。直接把配置文件写入共享卷，校验和 reload 交给代理程序 |

升级或重启管理界面时，nginx 会继续处理流量。新的 nginx 镜像在启动 nginx 之前会先校验卷里的配置，不兼容时管理界面会显示出问题的文件和行。nginx 发布新版本后，nginx 镜像会自动重新构建、测试并发布，旧标签保持不变。

## 仓库

| 仓库 | 说明 |
| --- | --- |
| [app](https://github.com/nginx-manager/app) | 管理界面（Spring Boot）、nginx 镜像和代理程序（Go）、安装包、发行说明 |

## 发行版本

版本以 git 标签（`vX.Y.Z`）管理，从 1.0.0 开始。每个版本的变更和截图整理在[发行说明](https://github.com/nginx-manager/app/blob/main/docs/releases/README.md)（韩语）和 [GitHub Releases](https://github.com/nginx-manager/app/releases) 中。当前使用的版本显示在管理界面底部（footer）。

<!-- releases:start -->
| 版本 | 日期 | 发行说明 |
| --- | --- | --- |
| v1.9.1 | 2026-10-31 | [v1.9.1](https://github.com/nginx-manager/app/blob/main/docs/releases/v1.9.1.md) |
| v1.9.0 | 2026-10-30 | [v1.9.0](https://github.com/nginx-manager/app/blob/main/docs/releases/v1.9.0.md) |
| v1.8.0 | 2026-10-30 | [v1.8.0](https://github.com/nginx-manager/app/blob/main/docs/releases/v1.8.0.md) |
| v1.7.0 | 2026-10-30 | [v1.7.0](https://github.com/nginx-manager/app/blob/main/docs/releases/v1.7.0.md) |
| v1.6.0 | 2026-10-30 | [v1.6.0](https://github.com/nginx-manager/app/blob/main/docs/releases/v1.6.0.md) |
| v1.5.0 | 2026-10-30 | [v1.5.0](https://github.com/nginx-manager/app/blob/main/docs/releases/v1.5.0.md) |
| v1.4.0 | 2026-10-30 | [v1.4.0](https://github.com/nginx-manager/app/blob/main/docs/releases/v1.4.0.md) |
| v1.3.0 | 2026-10-30 | [v1.3.0](https://github.com/nginx-manager/app/blob/main/docs/releases/v1.3.0.md) |
| v1.2.3 | 2026-10-30 | [v1.2.3](https://github.com/nginx-manager/app/blob/main/docs/releases/v1.2.3.md) |
| v1.2.2 | 2026-10-30 | [v1.2.2](https://github.com/nginx-manager/app/blob/main/docs/releases/v1.2.2.md) |
| v1.2.1 | 2026-10-30 | [v1.2.1](https://github.com/nginx-manager/app/blob/main/docs/releases/v1.2.1.md) |
| v1.2.0 | 2026-10-30 | [v1.2.0](https://github.com/nginx-manager/app/blob/main/docs/releases/v1.2.0.md) |
| v1.1.0 | 2026-10-29 | [v1.1.0](https://github.com/nginx-manager/app/blob/main/docs/releases/v1.1.0.md) |
| v1.0.0 | 2026-10-29 | [v1.0.0](https://github.com/nginx-manager/app/blob/main/docs/releases/v1.0.0.md) |
<!-- releases:end -->
