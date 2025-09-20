# T1 HR Assistant API

FastAPI сервер для взаимодействия с HR и User агентами на основе LangGraph.

## Запуск сервера

### Установка зависимостей
```bash
uv sync
```

### Запуск
```bash
# Через uvicorn напрямую
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Или через скрипт
python run_server.py
```

Сервер будет доступен по адресу: http://localhost:8000

## Документация API

После запуска сервера документация доступна по адресам:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Основные эндпоинты

### 1. Проверка здоровья сервиса
```http
GET /health
```

**Ответ:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "agents_available": ["hr", "user"],
  "timestamp": "2024-01-01T12:00:00"
}
```

### 2. Информация об агентах
```http
GET /agents
```

**Ответ:**
```json
{
  "agents": [
    {
      "agent_type": "hr",
      "model": "Qwen2.5-72B-Instruct-AWQ",
      "base_url": "https://llm.t1v.scibox.tech/v1",
      "max_tokens": 512,
      "temperature": 0.7
    }
  ],
  "total_agents": 2
}
```

### 3. Универсальный чат с агентом
```http
POST /chat
```

**Тело запроса:**
```json
{
  "message": "Привет, как дела?",
  "agent_type": "hr",
  "conversation_id": "session_123",
  "temperature": 0.7,
  "max_tokens": 512
}
```

**Ответ:**
```json
{
  "response": "Привет! У меня все хорошо, спасибо!",
  "agent_type": "hr",
  "conversation_id": "session_123",
  "processing_time": 1.23,
  "tokens_used": null
}
```

### 4. Чат с HR агентом (упрощенный)
```http
POST /chat/hr
```

**Тело запроса:**
```json
{
  "message": "Расскажи о политике отпусков"
}
```

### 5. Чат с User агентом (упрощенный)
```http
POST /chat/user
```

**Тело запроса:**
```json
{
  "message": "Помоги с настройкой рабочего места"
}
```

### 6. История разговора
```http
GET /chat/history/{conversation_id}
```

## Примеры использования

### cURL
```bash
# Проверка здоровья
curl -X GET "http://localhost:8000/health"

# Чат с HR агентом
curl -X POST "http://localhost:8000/chat/hr" \
  -H "Content-Type: application/json" \
  -d '{"message": "Какие документы нужны для оформления отпуска?"}'

# Чат с User агентом
curl -X POST "http://localhost:8000/chat/user" \
  -H "Content-Type: application/json" \
  -d '{"message": "Как настроить VPN?"}'
```

### Python
```python
import requests

# Базовый URL
BASE_URL = "http://localhost:8000"

# Чат с HR агентом
response = requests.post(
    f"{BASE_URL}/chat/hr",
    json={"message": "Расскажи о корпоративной культуре"}
)
print(response.json())

# Чат с User агентом
response = requests.post(
    f"{BASE_URL}/chat/user",
    json={"message": "Помоги с настройкой почты"}
)
print(response.json())
```

### JavaScript/TypeScript
```javascript
// Чат с HR агентом
const response = await fetch('http://localhost:8000/chat/hr', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: 'Какие льготы предоставляет компания?'
  })
});

const data = await response.json();
console.log(data);
```

## Обработка ошибок

API возвращает структурированные ошибки в формате:

```json
{
  "error": "ValidationError",
  "message": "Ошибка валидации входных данных",
  "details": {
    "errors": [
      {
        "loc": ["body", "message"],
        "msg": "field required",
        "type": "value_error.missing"
      }
    ]
  }
}
```

### Коды ошибок:
- `400` - Неверный запрос
- `422` - Ошибка валидации
- `500` - Внутренняя ошибка сервера
- `503` - Сервис недоступен

## Конфигурация

Настройки приложения находятся в файле `.env`:

```env
SCIBOX_API_KEY=your_api_key_here
```

## Мониторинг и логирование

Сервер ведет подробные логи всех операций. Уровень логирования можно настроить в `main.py`.

## Безопасность

- В продакшене рекомендуется ограничить CORS origins
- Добавить аутентификацию и авторизацию
- Использовать HTTPS
- Ограничить размер запросов
