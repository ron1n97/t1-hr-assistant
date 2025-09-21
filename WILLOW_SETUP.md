# Настройка Willow Inference Server

## Описание

Willow Inference Server - это единый самохостимый сервер с ASR/STT, TTS и LLM, который использует CTranslate2 для Whisper и поддерживает кастомные TTS-голоса. Для русского языка можно задать язык в параметрах Whisper и подключить русские TTS-голоса Piper.

## Установка и запуск

### 1. Установка через Docker (рекомендуется)

```bash
# Клонируем репозиторий Willow
git clone https://github.com/pykeio/willow.git
cd willow

# Запускаем через Docker Compose
docker-compose up -d
```

### 2. Установка через pip

```bash
# Установка Willow
pip install willow-inference-server

# Запуск сервера
willow-server --host 0.0.0.0 --port 8001
```

### 3. Настройка для русского языка

```bash
# Запуск с поддержкой русского языка
willow-server \
  --host 0.0.0.0 \
  --port 8001 \
  --whisper-model whisper-large-v3 \
  --whisper-language ru \
  --whisper-task transcribe
```

## Конфигурация в проекте

### 1. Обновите .env файл

```env
# Существующие настройки
SCIBOX_API_KEY=your_scibox_api_key

# Настройки Willow Inference Server
WILLOW_SERVER_URL=http://localhost:8001
WILLOW_API_KEY=  # Оставьте пустым, если не требуется авторизация
```

### 2. Проверка работы сервера

```bash
# Проверка статуса сервера
curl http://localhost:8001/health

# Проверка доступных моделей
curl http://localhost:8001/v1/models
```

## Преимущества Willow над SciBox

### ✅ **Производительность:**
- Использует CTranslate2 для ускорения Whisper
- Работает на доступных GPU
- Оптимизирован для самохостинга

### ✅ **Поддержка форматов:**
- Больше аудио форматов (включая FLAC, OGG)
- Увеличенный лимит размера файла (100MB vs 25MB)
- Лучшая обработка длинных аудио

### ✅ **Гибкость:**
- Настройка языка транскрипции
- Кастомные TTS-голоса
- Поддержка WebRTC и WebSocket

### ✅ **Безопасность:**
- Полный контроль над данными
- Нет отправки аудио в облако
- Возможность работы в изолированной сети

## API Endpoints

### Транскрипция аудио

```bash
POST /v1/audio/transcriptions
Content-Type: multipart/form-data

Parameters:
- file: аудио файл
- model: whisper (по умолчанию)
- language: ru (русский)
- task: transcribe
- response_format: json
```

### Пример запроса

```bash
curl -X POST "http://localhost:8001/v1/audio/transcriptions" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@audio.mp3" \
  -F "model=whisper" \
  -F "language=ru" \
  -F "task=transcribe" \
  -F "response_format=json"
```

## Мониторинг и логи

### Логи сервера

```bash
# Просмотр логов Docker контейнера
docker-compose logs -f willow

# Логи приложения
tail -f /var/log/willow/server.log
```

### Метрики производительности

```bash
# Статус сервера
curl http://localhost:8001/metrics

# Информация о моделях
curl http://localhost:8001/v1/models
```

## Troubleshooting

### Проблема: Сервер не запускается

```bash
# Проверка портов
netstat -tulpn | grep 8001

# Проверка Docker
docker ps | grep willow
```

### Проблема: Медленная транскрипция

```bash
# Проверка GPU
nvidia-smi

# Запуск с GPU
willow-server --device cuda --host 0.0.0.0 --port 8001
```

### Проблема: Ошибки памяти

```bash
# Уменьшение размера модели
willow-server --whisper-model whisper-base --host 0.0.0.0 --port 8001
```

## Интеграция с проектом

После настройки Willow сервера, ваше приложение автоматически будет использовать его для транскрипции аудио вместо SciBox API.

### Проверка интеграции

```bash
# Тест транскрипции через API
curl -X POST "http://localhost:8000/audio/transcriptions" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_audio.mp3" \
  -F "agent_type=user" \
  -F "conversation_id=test123"
```

## Дополнительные возможности

### TTS (Text-to-Speech)

```bash
# Запуск с поддержкой TTS
willow-server \
  --host 0.0.0.0 \
  --port 8001 \
  --tts-model piper \
  --tts-voice ru_RU-dmitri-medium
```

### WebSocket поддержка

```javascript
// Подключение через WebSocket
const ws = new WebSocket('ws://localhost:8001/ws');
ws.send(JSON.stringify({
  type: 'transcribe',
  audio: audioData,
  language: 'ru'
}));
```

## Заключение

Willow Inference Server предоставляет более эффективное и гибкое решение для транскрипции аудио по сравнению с внешними API. Он особенно подходит для проектов, требующих:

- Высокой производительности
- Контроля над данными
- Поддержки русского языка
- Работы в изолированной среде
