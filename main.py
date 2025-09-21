import time
import logging
import httpx
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
from user.profile_api import router as profile_router
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

# Подключение роутеров
app.include_router(profile_router)


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
        logger.info(f"📨 Получен запрос к агенту {request.agent_type}: '{request.message[:100]}...'")
        
        # Получаем агента
        agent = get_agent(request.agent_type)
        logger.info(f"🤖 Агент {request.agent_type} получен")
        
        # Обрабатываем запрос
        agent_start_time = time.time()
        if request.agent_type == AgentType.HR:
            logger.info(f"🔄 Запуск HR мультиагентной системы")
            response_text = agent.process_hr_request(request.message)
        else:
            logger.info(f"🔄 Запуск User агента")
            response_text = agent.process_user_request(request.message)
        
        agent_processing_time = time.time() - agent_start_time
        total_processing_time = time.time() - start_time
        
        logger.info(f"✅ Агент {request.agent_type} обработал запрос за {agent_processing_time:.2f}с")
        logger.info(f"📊 Общее время обработки: {total_processing_time:.2f}с")
        
        return ChatResponse(
            response=response_text,
            agent_type=request.agent_type,
            conversation_id=request.conversation_id,
            processing_time=total_processing_time
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


async def transcribe_audio_with_whisper(file_path: str, file_extension: str) -> str:
        """
        Отправляет аудио файл на Whisper сервер для транскрипции
        """
    # Определяем MIME тип на основе расширения файла
    mime_types = {
        '.mp3': 'audio/mpeg',
        '.mp4': 'audio/mp4',
        '.mpeg': 'audio/mpeg',
        '.mpga': 'audio/mpeg',
        '.m4a': 'audio/mp4',
        '.wav': 'audio/wav',
        '.webm': 'audio/webm',
        '.flac': 'audio/flac',
        '.ogg': 'audio/ogg'
    }
    
    mime_type = mime_types.get(file_extension.lower(), 'audio/mpeg')
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            with open(file_path, 'rb') as audio_file:
                files = {
                    'file': ('audio', audio_file, mime_type)
                }
                
                        # Параметры для Whisper сервера
                        data = {
                            'language': 'ru',    # Язык - русский
                            'response_format': 'json'  # Формат ответа
                        }
                
                # Заголовки для Willow
                headers = {}
                if settings.willow_api_key:
                    headers['Authorization'] = f'Bearer {settings.willow_api_key}'
                
                        logger.info(f"Отправка аудио файла на Whisper сервер: {file_path} (тип: {mime_type})")
                        logger.info(f"Whisper сервер URL: {settings.willow_server_url}")
                
                response = await client.post(
                    f'{settings.willow_server_url}/v1/audio/transcriptions',
                    files=files,
                    data=data,
                    headers=headers
                )
                
                logger.info(f"Ответ от Whisper сервера: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    transcribed_text = result.get('text', '')
                    logger.info(f"Транскрипция успешна, длина текста: {len(transcribed_text)} символов")
                    return transcribed_text
                elif response.status_code == 401:
                    logger.error("Ошибка авторизации при транскрипции через Whisper")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Ошибка авторизации при транскрипции аудио через Whisper сервер"
                    )
                elif response.status_code == 413:
                    logger.error("Файл слишком большой для транскрипции")
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="Аудио файл слишком большой. Максимальный размер: 100MB"
                    )
                elif response.status_code == 400:
                    logger.error(f"Ошибка валидации Whisper: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Ошибка валидации аудио файла: {response.text}"
                    )
                elif response.status_code == 503:
                    logger.error("Whisper сервер недоступен")
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Whisper сервер недоступен. Проверьте, что сервер запущен."
                    )
                else:
                    logger.error(f"Ошибка транскрипции Whisper: {response.status_code} - {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Ошибка транскрипции аудио через Whisper: {response.text}"
                    )
                    
    except httpx.TimeoutException:
        logger.error("Таймаут при транскрипции аудио через Whisper")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Таймаут при транскрипции аудио через Whisper. Попробуйте файл меньшего размера."
        )
    except httpx.ConnectError:
        logger.error("Ошибка подключения к Whisper серверу")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Whisper сервер недоступен. Проверьте, что сервер запущен на {settings.willow_server_url}"
        )
    except Exception as e:
        logger.error(f"Неожиданная ошибка при транскрипции аудио через Whisper: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при транскрипции аудио через Whisper: {str(e)}"
        )


@app.post("/audio/transcriptions", response_model=AudioTranscriptionResponse)
async def create_audio_transcription(
    file: UploadFile = File(...),
    agent_type: str = Form(...),
    conversation_id: Optional[str] = Form(None)
):
        """
        Транскрипция аудио файла в текст через Whisper сервер
        
        - **file**: Аудио файл (поддерживаются форматы: mp3, mp4, mpeg, mpga, m4a, wav, webm, flac, ogg)
        - **agent_type**: Тип агента для обработки транскрибированного текста (hr или user)
        - **conversation_id**: Идентификатор сессии (опционально)
        
        Использует Whisper сервер для транскрипции на русском языке.
        Максимальный размер файла: 100MB.
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
        
        # Валидация типа файла (Willow поддерживает больше форматов)
        allowed_extensions = {'.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm', '.flac', '.ogg'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Неподдерживаемый формат файла: {file_extension}. Поддерживаемые форматы: {', '.join(allowed_extensions)}"
            )
        
        # Валидация размера файла (максимум 100MB для Willow Inference Server)
        max_file_size = 100 * 1024 * 1024  # 100MB в байтах
        content = await file.read()
        if len(content) > max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Файл слишком большой: {len(content)} байт. Максимальный размер: {max_file_size} байт (100MB)"
            )
        
        # Сохраняем файл во временную директорию
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
                    # Транскрибируем аудио через Whisper сервер
                    transcribed_text = await transcribe_audio_with_whisper(temp_file_path, file_extension)
            
            if not transcribed_text.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Не удалось транскрибировать аудио. Возможно, файл поврежден или не содержит речи."
                )
            
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
        
        Алиас для /audio/transcriptions для совместимости с OpenAI API.
        Использует Whisper сервер для транскрипции.
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
