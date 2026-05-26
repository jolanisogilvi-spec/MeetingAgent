# MeetingAgent Docker 安装与运行

本文说明如何用 Docker Compose 启动 MeetingAgent。Compose 会启动两个容器：

- `meetingagent-backend`：FastAPI 后端，容器内端口 `8000`
- `meetingagent-frontend`：Vite 前端，容器内端口 `8050`，并代理 `/api`、`/docs`、`/uploads` 到后端容器

## 1. 环境要求

| 组件 | 建议版本 | 说明 |
|---|---|---|
| Docker | 24+ | Windows 推荐 Docker Desktop |
| Docker Compose | v2+ | 使用 `docker compose` 命令 |

确认 Docker 可用：

```bash
docker --version
docker compose version
```

## 2. 默认端口启动

在项目根目录执行：

```bash
docker compose up -d --build
```

启动后访问：

```text
前端系统：http://localhost:8050
接口文档：http://localhost:8050/docs
健康检查：http://localhost:8050/api/health
```

查看容器状态：

```bash
docker compose ps
```

查看日志：

```bash
docker compose logs -f backend
docker compose logs -f frontend
```

停止服务：

```bash
docker compose down
```

## 3. 端口被占用时

默认会映射：

- 宿主机 `8000` -> 后端容器 `8000`
- 宿主机 `8050` -> 前端容器 `8050`

如果宿主机端口被占用，复制 `.env.example` 为 `.env` 并改端口：

```bash
cp .env.example .env
```

例如：

```env
BACKEND_PORT=18000
FRONTEND_PORT=18050
```

然后重新启动：

```bash
docker compose up -d --build
```

此时访问：

```text
http://localhost:18050
```

PowerShell 也可以临时指定端口：

```powershell
$env:BACKEND_PORT="18000"
$env:FRONTEND_PORT="18050"
docker compose up -d --build
```

## 4. 局域网访问

前端容器监听 `0.0.0.0`，其他设备可通过宿主机局域网 IP 访问：

```text
http://<宿主机局域网IP>:8050
```

如果改过 `FRONTEND_PORT`，使用改后的端口，例如：

```text
http://<宿主机局域网IP>:18050
```

Windows 如果被防火墙拦截，可以用管理员 PowerShell 放行前端端口：

```powershell
netsh advfirewall firewall add rule name="MeetingAgent 8050" dir=in action=allow protocol=TCP localport=8050
```

如果使用了自定义端口，把命令中的 `8050` 换成实际的 `FRONTEND_PORT`。

## 5. 数据持久化

Compose 会把后端运行时数据挂载到宿主机：

```text
backend/data/
```

该目录包含：

- `app.db`：SQLite 数据库
- `uploads/`：会议材料、知识库文件、会前准备文件
- `exports/`：导出的 Word 文件

备份时复制整个 `backend/data/` 即可。

本地语音识别模型缓存保存在 Docker 命名卷 `meetingagent-model-cache`，避免重复下载 Whisper 模型。

## 6. 重建与清理

仅重建镜像并启动：

```bash
docker compose up -d --build
```

停止并删除容器，保留数据库和模型缓存：

```bash
docker compose down
```

停止并删除容器、模型缓存卷：

```bash
docker compose down -v
```

注意：`docker compose down -v` 会删除模型缓存卷，但不会删除宿主机上的 `backend/data/`。

## 7. 常见问题

- **前端能打开但接口 502/失败**：执行 `docker compose ps`，确认 `backend` 是 `healthy`。
- **模型测试失败 401**：进入设置页重新填写 API Key，并先点击对应模型卡片的“测试连接”。
- **本地语音模型首次很慢**：首次会下载模型，完成后会缓存在 `meetingagent-model-cache`。
- **局域网无法访问**：确认使用宿主机局域网 IP，不要使用 `localhost`；同时检查防火墙是否放行前端端口。
