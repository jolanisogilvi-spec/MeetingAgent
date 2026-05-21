"""Settings endpoints: GET (masked), PUT per-category, POST test/*."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.settings import Settings
from ..schemas.settings import (
    EmbeddingSettingsUpdate,
    EmbeddingTestRequest,
    LLMSettingsUpdate,
    LLMTestRequest,
    SettingsOut,
    SpeechSettingsUpdate,
    SpeechTestRequest,
    TestResult,
)
from ..services import embedding as embedding_service
from ..services import llm as llm_service
from ..services import speech as speech_service
from ..utils.ids import mask_key, now_iso

router = APIRouter(prefix="/settings", tags=["系统设置"])


def _get_or_create(db: Session) -> Settings:
    settings = db.get(Settings, 1)
    if settings is None:
        settings = Settings(id=1, updated_at=now_iso())
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def _to_output(settings: Settings) -> SettingsOut:
    return SettingsOut(
        llm_api_key=mask_key(settings.llm_api_key),
        llm_base_url=settings.llm_base_url,
        llm_model_name=settings.llm_model_name,
        embedding_api_key=mask_key(settings.embedding_api_key),
        embedding_base_url=settings.embedding_base_url,
        embedding_model_name=settings.embedding_model_name,
        speech_provider=settings.speech_provider,
        speech_model_type=settings.speech_model_type,
        speech_api_key=mask_key(settings.speech_api_key),
        speech_base_url=settings.speech_base_url,
        speech_model_name=settings.speech_model_name,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
        updated_at=settings.updated_at,
    )


def _apply(settings: Settings, data: dict) -> None:
    for key, value in data.items():
        if value is None:
            continue
        setattr(settings, key, value)
    settings.updated_at = now_iso()


@router.get("", response_model=SettingsOut, summary="获取系统设置", description="获取模型配置。返回结果会对 API Key 进行脱敏。")
def get_settings(db: Session = Depends(get_db)) -> SettingsOut:
    settings = _get_or_create(db)
    return _to_output(settings)


@router.put("/llm", response_model=SettingsOut, summary="保存大模型配置", description="保存用于摘要、结构化纪要和质检补全的大模型配置。API Key 留空时保持原值不变。")
def update_llm(payload: LLMSettingsUpdate, db: Session = Depends(get_db)) -> SettingsOut:
    settings = _get_or_create(db)
    _apply(settings, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(settings)
    return _to_output(settings)


@router.put("/embedding", response_model=SettingsOut, summary="保存 Embedding 配置", description="保存知识库检索使用的 Embedding 模型配置。API Key 留空时保持原值不变。")
def update_embedding(
    payload: EmbeddingSettingsUpdate, db: Session = Depends(get_db)
) -> SettingsOut:
    settings = _get_or_create(db)
    _apply(settings, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(settings)
    return _to_output(settings)


@router.put("/speech", response_model=SettingsOut, summary="保存语音模型配置", description="保存语音转写配置。选择本地模式时会清空线上语音 API Key 和 Base URL。")
def update_speech(
    payload: SpeechSettingsUpdate, db: Session = Depends(get_db)
) -> SettingsOut:
    settings = _get_or_create(db)
    data = payload.model_dump(exclude_unset=True)
    _apply(settings, data)
    if settings.speech_provider == "local":
        settings.speech_api_key = ""
        settings.speech_base_url = ""
    db.commit()
    db.refresh(settings)
    return _to_output(settings)


@router.post("/test/llm", response_model=TestResult, summary="测试大模型", description="向大模型发送简短请求，验证 API Key、Base URL 和模型 ID 是否可用。")
def test_llm(
    payload: LLMTestRequest | None = None, db: Session = Depends(get_db)
) -> TestResult:
    settings = _get_or_create(db)
    data = payload.model_dump(exclude_unset=True) if payload else {}
    result = llm_service.test_llm(
        api_key=data.get("llm_api_key") or settings.llm_api_key,
        base_url=data.get("llm_base_url") or settings.llm_base_url,
        model=data.get("llm_model_name") or settings.llm_model_name,
        temperature=data.get("temperature") if data.get("temperature") is not None else settings.temperature,
        max_tokens=data.get("max_tokens") if data.get("max_tokens") is not None else 32,
    )
    return TestResult(**result)


@router.post("/test/embedding", response_model=TestResult, summary="测试 Embedding", description="请求一条测试向量，验证 Embedding 配置并返回向量维度。")
def test_embedding(
    payload: EmbeddingTestRequest | None = None, db: Session = Depends(get_db)
) -> TestResult:
    settings = _get_or_create(db)
    data = payload.model_dump(exclude_unset=True) if payload else {}
    result = embedding_service.test_embedding(
        api_key=data.get("embedding_api_key") or settings.embedding_api_key,
        base_url=data.get("embedding_base_url") or settings.embedding_base_url,
        model=data.get("embedding_model_name") or settings.embedding_model_name,
    )
    return TestResult(**result)


@router.post("/test/speech", response_model=TestResult, summary="测试语音模型", description="本地模式会尝试加载 Whisper 模型；线上模式会测试接口连通性。")
def test_speech(
    payload: SpeechTestRequest | None = None, db: Session = Depends(get_db)
) -> TestResult:
    settings = _get_or_create(db)
    data = payload.model_dump(exclude_unset=True) if payload else {}
    result = speech_service.test_speech(
        provider=data.get("speech_provider") or settings.speech_provider,
        model_type=data.get("speech_model_type") or settings.speech_model_type,
        api_key=data.get("speech_api_key") or settings.speech_api_key,
        base_url=data.get("speech_base_url") or settings.speech_base_url,
        model_name=data.get("speech_model_name") or settings.speech_model_name,
    )
    return TestResult(**result)
