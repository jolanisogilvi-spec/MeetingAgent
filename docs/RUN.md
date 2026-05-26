# MeetingAgent 启动说明

## 1. 环境要求

| 组件 | 版本 | 说明 |
|---|---|---|
| Python | 3.10+ | 推荐 3.10 / 3.11 / 3.12 |
| Node.js | 18+ | 推荐 18 LTS 或 20 LTS |
| 操作系统 | Linux / macOS / Windows (WSL) | |
| 浏览器 | Chrome / Edge / Firefox 最新版 | |

## 2. 后端启动

```bash
cd backend

# 建议使用虚拟环境
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt

# 开发模式启动（带热重载）
uvicorn app.main:app --reload --port 8000
# 或直接：python -m app.main
```

启动后：

- API 根：http://localhost:8000/api
- 健康检查：http://localhost:8000/api/health
- 交互文档（Swagger UI）：http://localhost:8000/docs
- ReDoc 文档：http://localhost:8000/redoc

首次启动会自动在 `backend/data/` 下创建：

- `app.db` — SQLite 数据库
- `uploads/<meeting_id>/` — 上传的会议材料与知识库文件
- `exports/` — 导出的 Word 文件

## 3. 前端启动

```bash
cd frontend
npm install
npm run dev
```

浏览器访问 http://localhost:8050

Vite 已配置代理：所有 `/api/*` 请求会转发到 `http://localhost:8000`，因此前后端可以分别启动。

生产构建：
```bash
npm run build      # 输出到 frontend/dist
npm run preview    # 本地预览构建产物
```

## 4. Docker 启动

项目已提供 Docker Compose 配置。默认启动：

```bash
docker compose up -d --build
```

浏览器访问：

```text
http://localhost:8050
```

如果需要局域网访问，使用宿主机局域网 IP：

```text
http://<宿主机局域网IP>:8050
```

如果 `8000` 或 `8050` 被占用，复制 `.env.example` 为 `.env` 并修改：

```env
BACKEND_PORT=18000
FRONTEND_PORT=18050
```

然后重新执行：

```bash
docker compose up -d --build
```

更完整的 Docker 说明见 [DOCKER.md](DOCKER.md)。

## 5. 首次使用流程

按以下顺序操作可以最快验证整套链路：

1. **设置（左侧导航 → 设置）**
   - 大模型卡片：填写兼容 OpenAI 协议的 API Key / Base URL / 模型 ID（如 DeepSeek、Qwen、智谱、OpenAI 等）→ 保存 → 点击"测试连接"，应在卡片内显示"模型可用"。
   - Embedding 卡片：填写 Embedding 服务 API Key / Base URL / 模型 ID → 保存 → 测试 → 应返回向量维度。
   - 语音模型卡片：选择"本地"或"线上"。本地选 Whisper 模型名（如 `base` / `small` / `medium`），测试会尝试加载；线上则填写 API Key / Base URL / 模型 ID。
2. **人员与部门（左侧导航 → 人员与部门）**
   - 在左栏"新增部门"，例如"产品部"。
   - 在右栏"新增人员"，绑定部门，例如"张三 / 产品部 / 产品经理"。
3. **会议（左侧导航 → 会议）**
   - 点击"新建会议"，填写会议名称、所属部门、参会人员 → 创建后自动跳到会议详情。
   - 会议详情页"会议材料"：粘贴一段会议文本，或上传 `.mp3 / .wav / .txt / .docx`；可选上传若干 `.txt / .docx` 知识库参考资料。
   - 点击"生成会议纪要"，等待若干秒（取决于模型）。完成后在"结果"分页查看：摘要 / 结构化纪要 / 待办任务 / JSON 编辑 / 原文。
   - 在 JSON 编辑分页可以手动修改结构化纪要并保存，待办任务会基于 JSON 重新生成。
   - 点击右上角"导出 Word"，浏览器下载 `<会议名>.docx`。
4. **日程任务（左侧导航 → 日程任务）**
   - 汇总所有会议沉淀出的待办任务。
   - 支持按部门 / 责任人 / 会议 / 状态筛选；可在表格中内联编辑责任人、标题、截止时间、状态；删除前会要求确认。

## 6. 数据存储说明

| 路径 | 内容 |
|---|---|
| `backend/data/app.db` | SQLite 数据库，包含部门、人员、会议、任务、设置 |
| `backend/data/uploads/<meeting_id>/` | 该会议上传的所有材料；删除会议时整目录清空 |
| `backend/data/exports/` | Word 导出文件 |

备份只需复制整个 `backend/data/` 目录。重置只需删除该目录后重启后端。

## 7. 模型配置说明

- **大模型**：使用 OpenAI SDK 兼容协议（`openai.OpenAI(api_key=..., base_url=...)`），支持 DeepSeek、Qwen、Moonshot、智谱、OpenAI 等。`Base URL` 通常以 `/v1` 结尾。
- **Embedding**：同样使用 OpenAI 兼容协议。若你填的 Base URL 已经包含 `/embeddings`，后端会自动剥离避免拼出 `/embeddings/embeddings`。**不允许默认复用大模型 API Key / Base URL**，必须显式填写。
- **语音模型**：
  - 本地模式使用 `faster-whisper`，模型名可选 `tiny / base / small / medium / large-v3` 等；测试连接会尝试加载该模型（首次下载较慢）。
  - 线上模式调用任意 OpenAI 兼容 `/audio/transcriptions` 端点。

API Key 在保存后返回时会被屏蔽（仅保留前 4 位 + `****`），保存表单留空字段时不会覆盖已存在的 key。

## 8. 已知限制（第一版）

- 生成会议纪要已改为后台任务 + 前端轮询；当前还没有独立任务队列，服务进程重启会中断正在生成的任务。
- 向量索引为内存版（每次生成现切现算），不持久化；多次生成同一份知识库会重复计算。
- 任务无权限校验，所有用户可见全部数据。
- Word 导出样式较朴素，未做企业模板定制。
- 未提供登录与多租户隔离。

## 9. 故障排查

- **后端启动报缺包**：确认 `pip install -r requirements.txt` 已在当前 venv 内执行成功。
- **前端 `npm install` 卡住**：检查网络代理；可使用 `npm config set registry https://registry.npmmirror.com/` 切换镜像。
- **生成失败 401 / 鉴权失败**：在"设置"页重新填写 API Key 并先点"测试连接"通过再生成。
- **embedding 返回 404**：可能 Base URL 写错路径，确认是否要带 `/v1`；后端已对尾部 `/embeddings` 做规范化。
- **本地语音模型加载失败**：首次会从 HuggingFace 下载，确认网络；或先用 `tiny / base` 模型测试。
- **Word 导出 400 "请先生成会议纪要"**：该会议尚未生成纪要，先生成再导出。
