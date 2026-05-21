# MeetingAgent 技术架构约定

本文档是团队共同遵守的技术约定。所有 agent 必须按本文档进行开发，避免技术栈分歧。

## 1. 技术栈

### 后端
- **框架**: FastAPI
- **ASGI**: uvicorn
- **ORM**: SQLAlchemy 2.x (sync 模式即可)
- **数据库**: SQLite（开箱即用，文件位置 `backend/data/app.db`）
- **数据校验**: Pydantic v2
- **HTTP 客户端**: httpx
- **LLM 调用**: openai SDK (兼容所有 OpenAI 协议厂商，包括 DeepSeek/Qwen/智谱/Moonshot 等)
- **Embedding 调用**: openai SDK
- **语音识别(本地)**: faster-whisper
- **语音识别(线上)**: 使用 openai SDK / httpx 调用任意兼容接口
- **文档解析**: python-docx (docx)，直接读取 (txt)
- **Word 导出**: python-docx
- **向量检索**: numpy 余弦相似度（第一版无需 FAISS）
- **依赖管理**: requirements.txt
- **Python 版本**: 3.10+

### 前端
- **框架**: Vue 3 + `<script setup>` 语法
- **构建**: Vite
- **路由**: vue-router 4
- **状态**: Pinia
- **UI 库**: Element Plus
- **HTTP**: axios
- **图标**: @element-plus/icons-vue
- **样式**: scoped CSS + 少量全局变量

### 部署形态
- 前端独立 dev 服务器 (vite, 端口 8050)
- 后端 FastAPI 服务 (端口 8000)
- 前端通过 axios 调用 `/api/*`，vite 配置代理到后端

## 2. 目录结构

```
MeetingAgent/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI 入口
│   │   ├── config.py              # 配置（路径、上传目录等）
│   │   ├── database.py            # SQLAlchemy session 与初始化
│   │   ├── models/                # SQLAlchemy ORM 模型
│   │   │   ├── __init__.py
│   │   │   ├── department.py
│   │   │   ├── person.py
│   │   │   ├── meeting.py
│   │   │   ├── task.py
│   │   │   └── settings.py
│   │   ├── schemas/               # Pydantic 请求/响应
│   │   │   ├── __init__.py
│   │   │   ├── department.py
│   │   │   ├── person.py
│   │   │   ├── meeting.py
│   │   │   ├── task.py
│   │   │   └── settings.py
│   │   ├── api/                   # 路由
│   │   │   ├── __init__.py
│   │   │   ├── health.py
│   │   │   ├── departments.py
│   │   │   ├── people.py
│   │   │   ├── meetings.py
│   │   │   ├── tasks.py
│   │   │   └── settings.py
│   │   ├── services/              # 业务逻辑 / AI 工作流
│   │   │   ├── __init__.py
│   │   │   ├── llm.py             # 大模型客户端
│   │   │   ├── embedding.py       # Embedding 客户端
│   │   │   ├── speech.py          # 语音识别
│   │   │   ├── rag.py             # 知识库检索
│   │   │   ├── meeting_ai.py      # 摘要/结构化/质检 三步工作流
│   │   │   ├── file_parser.py     # txt/docx 解析
│   │   │   └── exporter.py        # Word 导出
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── ids.py             # ID 生成
│   ├── data/                      # SQLite + 上传文件（运行时生成）
│   │   ├── app.db
│   │   ├── uploads/
│   │   └── exports/
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── router/index.js
│   │   ├── stores/                # Pinia
│   │   │   ├── meetings.js
│   │   │   ├── people.js
│   │   │   ├── departments.js
│   │   │   ├── tasks.js
│   │   │   └── settings.js
│   │   ├── api/index.js           # axios 实例 + 接口封装
│   │   ├── layouts/
│   │   │   └── MainLayout.vue     # 左侧导航 + 主区域
│   │   ├── views/
│   │   │   ├── meetings/
│   │   │   │   ├── MeetingList.vue
│   │   │   │   ├── MeetingDetail.vue
│   │   │   │   └── components/    # 详情子组件
│   │   │   ├── tasks/TaskList.vue
│   │   │   ├── org/PeopleAndDepartments.vue
│   │   │   └── settings/Settings.vue
│   │   └── styles/global.css
│   └── README.md
└── docs/
    ├── ARCHITECTURE.md            # 本文档
    └── RUN.md                     # 启动说明（最后补充）
```

## 3. 关键约定

### 3.1 ID 规则
- 所有 ID 字符串形如 `<prefix>_<8位随机>`
  - 部门: `dept_xxxxxxxx`
  - 人员: `person_xxxxxxxx`
  - 会议: `meeting_xxxxxxxx`
  - 任务: `task_xxxxxxxx`
- 使用 `backend/app/utils/ids.py` 提供的 `make_id(prefix)` 函数生成

### 3.2 时间字段
- 数据库使用 ISO 8601 字符串（保持简单一致）
- `created_at` / `updated_at` 由后端自动维护

### 3.3 错误返回格式
所有错误返回统一为：
```json
{ "detail": "可读的中文错误信息" }
```
HTTP 状态码遵循 REST 习惯（400 参数错误，404 未找到，500 内部错误）。

### 3.4 设置存储
Settings 使用单行表（id 固定为 1），通过 `GET /api/settings` 获取，分类 PUT 更新。
返回时 API Key 用 `mask_key()` 屏蔽（保留前 4 位 + `****`）。

### 3.5 文件上传
- 上传目录: `backend/data/uploads/<meeting_id>/`
- 类型校验:
  - 会议文件: `.mp3 .wav .txt .docx`
  - 知识库: `.txt .docx`
- 单文件上限 50MB

### 3.6 状态机
- Meeting status: `draft | generating | completed | confirmed | failed`
- Task status: `todo | doing | done | delayed`

### 3.7 AI 工作流
`meeting_ai.generate_minutes(meeting_id, settings)`：
1. 准备原文（来自 raw_text 或语音转写）
2. 解析 + 切分 + Embedding 知识库
3. 对全文检索 top-K 片段拼上下文
4. 调用 LLM 生成摘要
5. 调用 LLM 抽取 JSON（强制 JSON 输出）
6. 调用 LLM 质检补全 JSON
7. 写回 Meeting；根据 ActionItems 生成 Task 记录
8. 全程异常捕获，失败时 status=failed + error_message

### 3.8 LLM JSON 输出
- 优先使用 `response_format={"type":"json_object"}`
- 失败时提示词强制 "只输出 JSON，不要 markdown 代码块"
- 解析失败时尝试用正则提取 `{...}` 再 json.loads

### 3.9 Embedding Base URL 规范化
- 用户填 `https://api.x.com/v1` → 拼 `/embeddings`
- 用户填 `https://api.x.com/v1/embeddings` → 保留原样
- openai SDK 传 `base_url` 时只传到 `/v1` 层级
- 实现位于 `backend/app/services/embedding.py`

### 3.10 前端 API 封装
所有 axios 调用统一在 `frontend/src/api/index.js`，错误统一通过 ElMessage 提示。
基础地址 `/api`，开发环境 vite 代理到 `http://localhost:8000`。

### 3.11 前端反馈规则
- 长任务按钮使用 `loading` 状态
- 模型测试结果显示在卡片内 `<el-alert>` 而非全局通知
- 创建/删除统一 `ElMessage.success` / `ElMessage.error`
- 删除前 `ElMessageBox.confirm`

## 4. 运行方式（最终交付）

后端：
```
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

前端：
```
cd frontend
npm install
npm run dev
```

打开 http://localhost:8050

## 5. 协作约束

- 每个 agent 只能修改属于自己模块的文件
- 共享文件（如 `requirements.txt`、`api/index.js`）需要在 task 评论里说明追加内容，避免冲突
- 创建文件前先确认是否已存在
- 改动 schema/数据模型 必须通知后端架构 agent
