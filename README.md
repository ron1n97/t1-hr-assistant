# T1 HR Assistant

Система агентов на основе LangGraph для HR и пользовательской поддержки.

## Описание

Проект содержит два типа агентов:
- **HR Agent** - для обработки HR-запросов
- **User Agent** - для пользовательской поддержки

Агенты используют модель Qwen2.5-72B-Instruct-AWQ через SciBox API.

## Структура проекта

```
t1-hr-assistant/
├── main.py                 # FastAPI сервер
├── models.py              # Pydantic модели
├── hr_agentic_system.py   # HR агент
├── user_agentic_system.py # User агент
├── config.py              # Конфигурация
├── test_llm.py           # Тест агентов
├── test_api.py           # Тест API
├── run_server.py         # Скрипт запуска сервера
├── API_USAGE.md          # Документация API
└── pyproject.toml        # Зависимости
```

## Быстрый старт

### 1. Установка зависимостей

```bash
# Установка uv (если не установлен)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Установка зависимостей проекта
uv sync
```

### 2. Настройка окружения

Создайте файл `.env`:
```env
SCIBOX_API_KEY=your_api_key_here
```

### 3. Запуск сервера

```bash
# Через uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Или через скрипт
python run_server.py
```

Сервер будет доступен по адресу: http://localhost:8000

### 4. Тестирование

```bash
# Тест агентов напрямую
python test_llm.py

# Тест API
python test_api.py
```

## API Документация

После запуска сервера документация доступна по адресам:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Подробная документация API находится в файле [API_USAGE.md](API_USAGE.md).

## Основные эндпоинты

- `GET /health` - Проверка здоровья сервиса
- `GET /agents` - Информация об агентах
- `POST /chat` - Универсальный чат с агентом
- `POST /chat/hr` - Чат с HR агентом
- `POST /chat/user` - Чат с User агентом

## Пример использования

### Через API

```bash
# Чат с HR агентом
curl -X POST "http://localhost:8000/chat/hr" \
  -H "Content-Type: application/json" \
  -d '{"message": "Какие документы нужны для отпуска?"}'

# Чат с User агентом
curl -X POST "http://localhost:8000/chat/user" \
  -H "Content-Type: application/json" \
  -d '{"message": "Помоги с настройкой VPN"}'
```

### Через Python

```python
from hr_agentic_system import HRRequestServer
from user_agentic_system import UserRequestServer

# HR агент
hr_response = HRRequestServer.process_hr_request("Расскажи о политике отпусков")
print(hr_response)

# User агент
user_response = UserRequestServer.process_user_request("Помоги с настройкой почты")
print(user_response)
```

## Разработка

### Установка зависимостей для разработки

```bash
uv sync --group dev
```

### Форматирование кода

```bash
uv run black .
```

### Структура агентов

Каждый агент построен на основе LangGraph и содержит:
- StateGraph для управления состоянием
- ChatOpenAI для взаимодействия с LLM
- Обработчик сообщений

## Конфигурация

Настройки приложения:
- `SCIBOX_API_KEY` - API ключ для SciBox
- Модель: Qwen2.5-72B-Instruct-AWQ
- Базовый URL: https://llm.t1v.scibox.tech/v1
- Температура: 0.7
- Максимальные токены: 512

## Мониторинг

Сервер ведет подробные логи всех операций. Для продакшена рекомендуется:
- Настроить централизованное логирование
- Добавить метрики (Prometheus/Grafana)
- Настроить мониторинг здоровья

## Безопасность

- Ограничить CORS origins в продакшене
- Добавить аутентификацию
- Использовать HTTPS
- Валидировать входные данные

## Лицензия

Проект разработан для внутреннего использования T1.
