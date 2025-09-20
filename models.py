from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class AgentType(str, Enum):
    """Типы доступных агентов"""
    HR = "hr"
    USER = "user"


class ChatRequest(BaseModel):
    """Модель запроса для чата с агентом"""
    message: str = Field(
        ..., 
        min_length=1, 
        max_length=4000,
        description="Сообщение пользователя для обработки агентом"
    )
    agent_type: AgentType = Field(
        ..., 
        description="Тип агента для обработки запроса"
    )
    conversation_id: Optional[str] = Field(
        None, 
        max_length=100,
        description="Идентификатор сессии для поддержания контекста разговора"
    )
    temperature: Optional[float] = Field(
        None, 
        ge=0.0, 
        le=2.0,
        description="Температура для генерации ответа (0.0 - детерминированно, 2.0 - очень креативно)"
    )
    max_tokens: Optional[int] = Field(
        None, 
        ge=50, 
        le=2000,
        description="Максимальное количество токенов в ответе"
    )

    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Сообщение не может быть пустым')
        return v.strip()


class ChatResponse(BaseModel):
    """Модель ответа от агента"""
    response: str = Field(..., description="Ответ агента")
    agent_type: AgentType = Field(..., description="Тип агента, который обработал запрос")
    conversation_id: Optional[str] = Field(None, description="Идентификатор сессии")
    processing_time: float = Field(..., description="Время обработки запроса в секундах")
    tokens_used: Optional[int] = Field(None, description="Количество использованных токенов")


class HealthResponse(BaseModel):
    """Модель ответа для проверки здоровья сервиса"""
    status: str = Field(..., description="Статус сервиса")
    version: str = Field(..., description="Версия приложения")
    agents_available: List[AgentType] = Field(..., description="Доступные типы агентов")
    timestamp: str = Field(..., description="Время проверки")


class ErrorResponse(BaseModel):
    """Модель ответа при ошибке"""
    error: str = Field(..., description="Тип ошибки")
    message: str = Field(..., description="Описание ошибки")
    details: Optional[Dict[str, Any]] = Field(None, description="Дополнительные детали ошибки")


class AgentInfo(BaseModel):
    """Информация об агенте"""
    agent_type: AgentType = Field(..., description="Тип агента")
    model: str = Field(..., description="Используемая модель")
    base_url: str = Field(..., description="Базовый URL для API")
    max_tokens: int = Field(..., description="Максимальное количество токенов")
    temperature: float = Field(..., description="Температура генерации")


class AgentsInfoResponse(BaseModel):
    """Информация о всех доступных агентах"""
    agents: List[AgentInfo] = Field(..., description="Список доступных агентов")
    total_agents: int = Field(..., description="Общее количество агентов")
