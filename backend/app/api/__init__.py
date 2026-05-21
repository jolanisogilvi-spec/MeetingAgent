"""Aggregate all API routers under a single `api_router`."""
from fastapi import APIRouter

from .departments import router as departments_router
from .health import router as health_router
from .meetings import router as meetings_router
from .people import router as people_router
from .settings import router as settings_router
from .tasks import router as tasks_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(departments_router)
api_router.include_router(people_router)
api_router.include_router(meetings_router)
api_router.include_router(tasks_router)
api_router.include_router(settings_router)
