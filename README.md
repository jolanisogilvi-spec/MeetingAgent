# MeetingAgent

会议智能体系统，覆盖会议创建、材料汇总、AI 纪要生成、待办沉淀、Word 导出和组织资料维护。系统不包含登录模块，默认面向内网或本地部署使用。

后端使用 **FastAPI + SQLAlchemy + SQLite**，前端使用 **Vue 3 + Vite + Element Plus**。开发环境对外统一访问 `8050` 端口，前端会把接口和文档请求代理到后端服务。

## 访问入口

| 用途 | 地址 | 说明 |
|---|---|---|
| 前端系统 | http://localhost:8050 | 主入口 |
| 接口文档 | http://localhost:8050/docs | 中文 Swagger 文档 |
| OpenAPI JSON | http://localhost:8050/openapi.json | 接口元数据 |
| 健康检查 | http://localhost:8050/api/health | 通过前端代理访问后端 |

后端服务实际运行在 `8000` 端口，前端 Vite 服务运行在 `8050` 端口。日常使用只需要打开 `http://localhost:8050`。

## 主要功能

- 数据看板：汇总会议、任务、人员、部门等核心运营数据
- 会议管理：创建、筛选、查看和删除会议
- 会议详情：维护基础信息、参会人员、会议材料和知识库参考资料
- AI 纪要生成：摘要、结构化纪要、质检补全三步生成
- 待办沉淀：自动从纪要中抽取任务，并在日程任务页集中管理
- JSON 编辑：支持手动编辑结构化纪要并重新同步任务
- Word 导出：导出会议纪要文档，包含结构化内容和待办事项
- 组织管理：维护部门与人员资料
- 系统设置：分别配置和测试大模型、Embedding、语音模型
- 中文接口文档：FastAPI 文档已补齐中文分组、接口说明和字段说明

## 快速启动

### 1. 启动后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. 启动前端

新开一个终端：

```bash
cd frontend
npm install
npm run dev
```

打开：

```text
http://localhost:8050
```

前端右上角有“接口文档”按钮，会打开 `http://localhost:8050/docs`。

## 端口说明

| 服务 | 端口 | 对外建议访问 |
|---|---:|---|
| Vite 前端 | 8050 | 是 |
| FastAPI 后端 | 8000 | 否，建议通过 8050 代理访问 |

前端代理配置位于 `frontend/vite.config.js`：

- `/api/*` → `http://localhost:8000/api/*`
- `/docs` → `http://localhost:8000/docs`
- `/openapi.json` → `http://localhost:8000/openapi.json`
- `/redoc` → `http://localhost:8000/redoc`

## 页面路径

| 页面 | 路径 |
|---|---|
| 数据看板 | `/dashboard` |
| 会议列表 | `/meetings` |
| 会议详情 | `/meetings/:id` |
| 日程任务 | `/tasks` |
| 人员与部门 | `/org` |
| 设置 | `/settings` |
| 接口文档 | `/docs` |

## 目录结构

```text
MeetingAgent/
├── backend/                # FastAPI 后端
│   ├── app/
│   │   ├── main.py         # 后端入口与 OpenAPI 文档配置
│   │   ├── config.py       # 路径与运行参数
│   │   ├── database.py     # SQLAlchemy session
│   │   ├── models/         # ORM 模型
│   │   ├── schemas/        # Pydantic 请求/响应与字段说明
│   │   ├── api/            # REST 路由
│   │   ├── services/       # LLM / Embedding / 语音 / RAG / 导出
│   │   └── utils/          # ID 生成、时间、key 屏蔽
│   ├── data/               # 运行时生成：SQLite、上传文件、导出文件
│   └── requirements.txt
├── frontend/               # Vue 3 前端
│   ├── vite.config.js      # 8050 端口与代理配置
│   └── src/
│       ├── api/            # axios 封装与接口调用
│       ├── stores/         # Pinia
│       ├── router/         # vue-router
│       ├── layouts/        # 左侧导航与顶部工具区
│       ├── views/
│       │   ├── dashboard/  # 数据看板
│       │   ├── meetings/   # 会议列表与详情
│       │   ├── tasks/      # 日程任务
│       │   ├── org/        # 人员与部门
│       │   └── settings/   # 模型配置
│       └── styles/
└── docs/
    ├── ARCHITECTURE.md     # 技术架构与约定
    └── RUN.md              # 启动与故障排查
```

## 技术栈

| 层 | 选型 |
|---|---|
| 后端框架 | FastAPI + uvicorn |
| ORM | SQLAlchemy 2.x |
| 数据库 | SQLite |
| LLM / Embedding | openai SDK，兼容 OpenAI 协议 |
| 语音识别 | faster-whisper 或 OpenAI 兼容线上接口 |
| 文档解析 / 导出 | python-docx |
| 向量检索 | numpy 余弦相似度 |
| 前端框架 | Vue 3 |
| 构建 | Vite 5 |
| 状态 | Pinia |
| UI | Element Plus |
| HTTP | axios |

## 数据存储

运行时数据默认保存在 `backend/data/`：

| 路径 | 内容 |
|---|---|
| `backend/data/app.db` | SQLite 数据库 |
| `backend/data/uploads/<meeting_id>/` | 会议材料与知识库文件 |
| `backend/data/exports/` | 导出的 Word 文件 |

备份时复制整个 `backend/data/` 目录即可。重置数据时停止服务，删除该目录后重新启动后端。

## 验证方式

```bash
# 后端语法检查
cd backend
python -m compileall app

# 前端构建检查
cd frontend
npm run build
```

也可以直接访问：

- `http://localhost:8050/api/health` 应返回 `{"status":"ok"}`
- `http://localhost:8050/docs` 应显示“会议智能体 API”

## 已知限制

- 生成会议纪要使用后台任务和前端轮询；当前还没有独立任务队列，服务进程重启会中断正在生成的任务
- 向量索引为内存计算，不做持久化索引
- 系统没有登录、权限隔离和多租户能力
- Word 导出为基础样式，未接入企业模板

更详细的启动和排障说明见 [docs/RUN.md](docs/RUN.md)，架构约定见 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)。

## License

内部使用项目，未指定 License。
