"""Health check endpoint."""
from fastapi import APIRouter

router = APIRouter(tags=["健康检查"])


@router.get("/health", summary="健康检查", description="检查后端服务是否正常运行。")
def health() -> dict:
    return {"status": "ok"}
