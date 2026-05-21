"""Pydantic schemas for Settings."""
from pydantic import BaseModel, ConfigDict, Field


class LLMSettingsUpdate(BaseModel):
    llm_api_key: str | None = Field(default=None, description="大模型 API Key；留空时保持原值不变")
    llm_base_url: str | None = Field(default=None, description="大模型 Base URL，例如 https://api.example.com/v1")
    llm_model_name: str | None = Field(default=None, description="大模型 ID")
    temperature: float | None = Field(default=None, ge=0.0, le=2.0, description="采样温度，范围 0 到 2")
    max_tokens: int | None = Field(default=None, ge=1, le=32768, description="最大输出 token 数")


class EmbeddingSettingsUpdate(BaseModel):
    embedding_api_key: str | None = Field(default=None, description="Embedding API Key；留空时保持原值不变")
    embedding_base_url: str | None = Field(default=None, description="Embedding Base URL")
    embedding_model_name: str | None = Field(default=None, description="Embedding 模型 ID")


class SpeechSettingsUpdate(BaseModel):
    speech_provider: str | None = Field(default=None, pattern=r"^(local|online)$", description="语音识别模式：local 本地，online 线上")
    speech_model_type: str | None = Field(default=None, description="语音模型类型，例如 whisper")
    speech_api_key: str | None = Field(default=None, description="线上语音 API Key；本地模式不需要")
    speech_base_url: str | None = Field(default=None, description="线上语音接口 Base URL")
    speech_model_name: str | None = Field(default=None, description="语音模型名称，例如 base、small 或线上模型 ID")


class SettingsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    llm_api_key: str = Field(description="脱敏后的大模型 API Key")
    llm_base_url: str = Field(description="大模型 Base URL")
    llm_model_name: str = Field(description="大模型 ID")

    embedding_api_key: str = Field(description="脱敏后的 Embedding API Key")
    embedding_base_url: str = Field(description="Embedding Base URL")
    embedding_model_name: str = Field(description="Embedding 模型 ID")

    speech_provider: str = Field(description="语音识别模式：local 或 online")
    speech_model_type: str = Field(description="语音模型类型")
    speech_api_key: str = Field(description="脱敏后的语音 API Key")
    speech_base_url: str = Field(description="线上语音接口 Base URL")
    speech_model_name: str = Field(description="语音模型名称")

    temperature: float = Field(description="采样温度")
    max_tokens: int = Field(description="最大输出 token 数")
    updated_at: str = Field(description="设置更新时间，ISO 8601 字符串")


class LLMTestRequest(BaseModel):
    llm_api_key: str | None = Field(default=None, description="本次测试使用的大模型 API Key；留空则使用已保存配置")
    llm_base_url: str | None = Field(default=None, description="本次测试使用的大模型 Base URL")
    llm_model_name: str | None = Field(default=None, description="本次测试使用的大模型 ID")
    temperature: float | None = Field(default=None, description="本次测试使用的采样温度")
    max_tokens: int | None = Field(default=None, description="本次测试使用的最大输出 token 数")


class EmbeddingTestRequest(BaseModel):
    embedding_api_key: str | None = Field(default=None, description="本次测试使用的 Embedding API Key；留空则使用已保存配置")
    embedding_base_url: str | None = Field(default=None, description="本次测试使用的 Embedding Base URL")
    embedding_model_name: str | None = Field(default=None, description="本次测试使用的 Embedding 模型 ID")


class SpeechTestRequest(BaseModel):
    speech_provider: str | None = Field(default=None, description="本次测试使用的语音识别模式")
    speech_model_type: str | None = Field(default=None, description="本次测试使用的语音模型类型")
    speech_api_key: str | None = Field(default=None, description="本次测试使用的语音 API Key")
    speech_base_url: str | None = Field(default=None, description="本次测试使用的线上语音接口 Base URL")
    speech_model_name: str | None = Field(default=None, description="本次测试使用的语音模型名称")


class TestResult(BaseModel):
    ok: bool = Field(description="测试是否成功")
    message: str = Field(description="测试结果说明")
    extra: dict | None = Field(default=None, description="附加信息，例如模型回复或向量维度")
