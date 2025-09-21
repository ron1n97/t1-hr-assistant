import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import tempfile
import os

from models import (
    ChatRequest, 
    HRChatRequest,
    UserChatRequest,
    ChatResponse, 
    HealthResponse, 
    ErrorResponse, 
    AgentType,
    AgentsInfoResponse,
    AgentInfo,
    AudioTranscriptionRequest,
    AudioTranscriptionResponse
)
from hr.hr_agentic_system import HRRequestServer
from user.user_agentic_system import UserRequestServer
from config import Settings

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Глобальные переменные для хранения агентов
agents: Dict[AgentType, Any] = {}
settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Инициализация при запуске
    logger.info("Инициализация агентов...")
    try:
        agents[AgentType.HR] = HRRequestServer()
        agents[AgentType.USER] = UserRequestServer()
        logger.info("Агенты успешно инициализированы")
    except Exception as e:
        logger.error(f"Ошибка инициализации агентов: {e}")
        raise
    
    yield
    
    # Очистка при завершении
    logger.info("Завершение работы приложения...")


# Создание FastAPI приложения
app = FastAPI(
    title="T1 HR Assistant API",
    description="API для взаимодействия с HR и User агентами на основе LangGraph",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене следует ограничить домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Обработчики ошибок
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Обработка ошибок валидации"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="ValidationError",
            message="Ошибка валидации входных данных",
            details={"errors": exc.errors()}
        ).model_dump()
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Обработка HTTP исключений"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTPException",
            message=exc.detail
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Обработка общих исключений"""
    logger.error(f"Необработанная ошибка: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="InternalServerError",
            message="Внутренняя ошибка сервера"
        ).model_dump()
    )


# Зависимости
def get_agent(agent_type: AgentType):
    """Получение агента по типу"""
    if agent_type not in agents:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Агент {agent_type} недоступен"
        )
    return agents[agent_type]


# Эндпоинты
@app.get("/", response_model=Dict[str, str])
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "T1 HR Assistant API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Проверка здоровья сервиса"""
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        agents_available=list(agents.keys()),
        timestamp=datetime.now().isoformat()
    )


@app.get("/agents", response_model=AgentsInfoResponse)
async def get_agents_info():
    """Получение информации о доступных агентах"""
    agents_info = []
    
    for agent_type in AgentType:
        if agent_type in agents:
            # Получаем информацию о конфигурации агента
            agent_info = AgentInfo(
                agent_type=agent_type,
                model="Qwen2.5-72B-Instruct-AWQ",
                base_url="https://llm.t1v.scibox.tech/v1",
                max_tokens=512,
                temperature=0.7
            )
            agents_info.append(agent_info)
    
    return AgentsInfoResponse(
        agents=agents_info,
        total_agents=len(agents_info)
    )


@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """
    Основной эндпоинт для общения с агентами
    
    - **message**: Сообщение для обработки агентом
    - **agent_type**: Тип агента (hr или user)
    - **conversation_id**: Идентификатор сессии (опционально)
    - **temperature**: Температура генерации (опционально)
    - **max_tokens**: Максимальное количество токенов (опционально)
    """
    start_time = time.time()
    
    try:
        # Получаем агента
        agent = get_agent(request.agent_type)
        
        # Обрабатываем запрос
        if request.agent_type == AgentType.HR:
            response_text = agent.process_hr_request(request.message)
        else:
            response_text = agent.process_user_request(request.message)
        
        processing_time = time.time() - start_time
        
        logger.info(f"Запрос обработан за {processing_time:.2f}с агентом {request.agent_type}")
        
        return ChatResponse(
            response=response_text,
            agent_type=request.agent_type,
            conversation_id=request.conversation_id,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Ошибка обработки запроса: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка обработки запроса: {str(e)}"
        )


@app.post("/chat/hr", response_model=ChatResponse)
async def chat_with_hr_agent(request: HRChatRequest):
    """
    Эндпоинт для общения с HR агентом
    
    Удобный эндпоинт для быстрого доступа к HR агенту
    """
    # Создаем ChatRequest с установленным типом агента
    chat_request = ChatRequest(
        message=request.message,
        agent_type=AgentType.HR,
        conversation_id=request.conversation_id,
        temperature=request.temperature,
        max_tokens=request.max_tokens
    )
    return await chat_with_agent(chat_request)


@app.post("/chat/user", response_model=ChatResponse)
async def chat_with_user_agent(request: UserChatRequest):
    """
    Эндпоинт для общения с User агентом
    
    Удобный эндпоинт для быстрого доступа к User агенту
    """
    # Создаем ChatRequest с установленным типом агента
    chat_request = ChatRequest(
        message=request.message,
        agent_type=AgentType.USER,
        conversation_id=request.conversation_id,
        temperature=request.temperature,
        max_tokens=request.max_tokens
    )
    return await chat_with_agent(chat_request)


@app.get("/chat/history/{conversation_id}")
async def get_conversation_history(conversation_id: str):
    """
    Получение истории разговора по ID сессии
    
    В текущей реализации история не сохраняется, 
    но эндпоинт подготовлен для будущего расширения
    """
    # TODO: Реализовать сохранение и получение истории разговоров
    return {
        "conversation_id": conversation_id,
        "message": "История разговоров пока не реализована",
        "suggestions": [
            "Используйте conversation_id в запросах для будущего отслеживания",
            "История будет доступна в следующих версиях"
        ]
    }


@app.post("/audio/transcriptions", response_model=AudioTranscriptionResponse)
async def create_audio_transcription(
    file: UploadFile = File(...),
    agent_type: str = Form(...),
    conversation_id: Optional[str] = Form(None)
):
    """
    Транскрипция аудио файла в текст
    
    - **file**: Аудио файл (поддерживаются форматы: mp3, mp4, mpeg, mpga, m4a, wav, webm)
    - **agent_type**: Тип агента для обработки транскрибированного текста (hr или user)
    - **conversation_id**: Идентификатор сессии (опционально)
    """
    start_time = time.time()
    
    try:
        # Валидация типа агента
        try:
            agent_type_enum = AgentType(agent_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Неверный тип агента: {agent_type}. Доступные типы: hr, user"
            )
        
        # Валидация типа файла
        allowed_extensions = {'.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Неподдерживаемый формат файла: {file_extension}. Поддерживаемые форматы: {', '.join(allowed_extensions)}"
            )
        
        # Сохраняем файл во временную директорию
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Здесь должна быть интеграция с OpenAI Whisper API
            # Пока что возвращаем заглушку
            transcribed_text = f"Привет!"
            
            # Обрабатываем транскрибированный текст через агента
            agent = get_agent(agent_type_enum)
            
            if agent_type_enum == AgentType.HR:
                response_text = agent.process_hr_request(transcribed_text)
            else:
                response_text = agent.process_user_request(transcribed_text)
            
            processing_time = time.time() - start_time
            
            # Создаем ответ чата
            chat_response = ChatResponse(
                response=response_text,
                agent_type=agent_type_enum,
                conversation_id=conversation_id,
                processing_time=processing_time
            )
            
            logger.info(f"Аудио транскрибировано и обработано за {processing_time:.2f}с агентом {agent_type_enum}")
            
            return AudioTranscriptionResponse(
                text=transcribed_text,
                agent_type=agent_type_enum,
                conversation_id=conversation_id,
                processing_time=processing_time,
                chat_response=chat_response
            )
            
        finally:
            # Удаляем временный файл
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка транскрипции аудио: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка транскрипции аудио: {str(e)}"
        )


@app.post("/v1/audio/transcriptions", response_model=AudioTranscriptionResponse)
async def create_audio_transcription_v1(
    file: UploadFile = File(...),
    agent_type: str = Form(...),
    conversation_id: Optional[str] = Form(None)
):
    """
    Транскрипция аудио файла в текст (v1 API)
    
    Алиас для /audio/transcriptions для совместимости с OpenAI API
    """
    return await create_audio_transcription(file, agent_type, conversation_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
