"""FastAPI application entrypoint."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api import api_router
from .config import CORS_ORIGINS, UPLOAD_DIR, EXPORT_DIR, ensure_dirs
from .database import init_db

OPENAPI_TAGS = [
    {"name": "健康检查", "description": "服务存活状态检查。"},
    {"name": "部门管理", "description": "部门的创建、查询、更新和删除。"},
    {"name": "人员管理", "description": "人员资料维护，以及按部门筛选人员。"},
    {"name": "会议管理", "description": "会议创建、材料上传、AI 纪要生成、JSON 保存和 Word 导出。"},
    {"name": "任务管理", "description": "会议待办任务的查询、创建、编辑和删除。"},
    {"name": "系统设置", "description": "大模型、Embedding 和语音模型配置及连通性测试。"},
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="会议智能体 API",
    version="0.1.0",
    description=(
        "会议智能体后端接口文档。系统支持会议管理、人员与部门维护、"
        "AI 会议纪要生成、待办任务沉淀、模型配置测试和 Word 导出。"
    ),
    openapi_tags=OPENAPI_TAGS,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

ensure_dirs()
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.mount("/exports", StaticFiles(directory=str(EXPORT_DIR)), name="exports")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
