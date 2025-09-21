# 🐳 Простой запуск через Docker Compose

## 🚀 Быстрый старт

### 1. Настройка

```bash
# Скопируйте конфигурацию
cp env.example .env

# Отредактируйте .env файл
# Укажите ваш SCIBOX_API_KEY
```

### 2. Запуск

```bash
# Простой запуск (разработка)
./start.sh dev

# Или напрямую через Docker Compose
docker-compose up --build -d
```

## 🔧 Режимы работы

### Разработка (по умолчанию)
```bash
./start.sh dev
# или
docker-compose up --build -d
```

**Особенности:**
- ✅ Код монтируется в контейнер (hot reload)
- ✅ Встроенный Willow Inference Server
- ✅ Отладочные логи
- ✅ Автоматическая перезагрузка

### Продакшен
```bash
./start.sh prod
# или
ENVIRONMENT=production MOUNT_CODE=ro docker-compose up --build -d
```

**Особенности:**
- ✅ Код не монтируется (безопасность)
- ✅ Оптимизированная производительность
- ✅ Встроенный Willow Inference Server
- ✅ GPU поддержка (если доступна)

### С локальным Willow
```bash
./start.sh local
# или
WILLOW_SERVER_URL=http://host.docker.internal:8001 docker-compose up --build -d
```

**Особенности:**
- ✅ Использует локальный Willow сервер
- ✅ Код монтируется в контейнер
- ✅ Подходит для отладки транскрипции

## 📋 Управление

### Основные команды

```bash
# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Логи
docker-compose logs -f

# Статус
docker-compose ps

# Очистка
docker-compose down -v
```

### Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Только API
docker-compose logs -f t1-hr-assistant

# Только Willow
docker-compose logs -f willow-inference-server

# Только Frontend
docker-compose logs -f t1-hr-frontend
```

## 🧪 Тестирование

### Проверка здоровья

```bash
# API
curl http://localhost:8000/health

# Willow
curl http://localhost:8001/health

# Frontend
curl http://localhost:3000
```

### Тест API

```bash
# HR агент
curl -X POST "http://localhost:8000/chat/hr" \
  -H "Content-Type: application/json" \
  -d '{"message": "Найди кандидатов на позицию разработчика"}'

# User агент
curl -X POST "http://localhost:8000/chat/user" \
  -H "Content-Type: application/json" \
  -d '{"message": "Привет!"}'
```

### Тест транскрипции

```bash
# Загрузите аудио файл
curl -X POST "http://localhost:8000/audio/transcriptions" \
  -F "file=@audio.mp3" \
  -F "agent_type=user" \
  -F "conversation_id=test123"
```

## ⚙️ Конфигурация

### Переменные окружения (.env)

```env
# Основные настройки
SCIBOX_API_KEY=your_api_key_here

# Willow сервер
WILLOW_SERVER_URL=http://willow-inference-server:8001
WILLOW_WHISPER_MODEL=whisper-large-v3
WILLOW_WHISPER_LANGUAGE=ru
WILLOW_DEVICE=cpu

# Режим работы
ENVIRONMENT=development
MOUNT_CODE=z
```

### Настройка для GPU

```env
# В .env файле
WILLOW_DEVICE=cuda
```

**Требования:**
- NVIDIA GPU с CUDA
- nvidia-docker2
- Docker с GPU поддержкой

### Настройка модели Whisper

```env
# Быстрая модель (меньше точность)
WILLOW_WHISPER_MODEL=whisper-base

# Средняя модель
WILLOW_WHISPER_MODEL=whisper-medium

# Точная модель (по умолчанию)
WILLOW_WHISPER_MODEL=whisper-large-v3
```

## 🔍 Мониторинг

### Статус сервисов

```bash
# Общий статус
docker-compose ps

# Детальная информация
docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
```

### Использование ресурсов

```bash
# Статистика контейнеров
docker stats

# Использование диска
docker system df
```

### Логи с фильтрацией

```bash
# Только ошибки
docker-compose logs | grep ERROR

# Только Willow
docker-compose logs willow-inference-server

# Последние 100 строк
docker-compose logs --tail=100
```

## 🛠️ Troubleshooting

### Проблема: Контейнеры не запускаются

```bash
# Проверка логов
docker-compose logs

# Проверка конфигурации
docker-compose config

# Пересборка
docker-compose build --no-cache
```

### Проблема: Willow не отвечает

```bash
# Проверка логов Willow
docker-compose logs willow-inference-server

# Проверка портов
netstat -tulpn | grep 8001

# Перезапуск только Willow
docker-compose restart willow-inference-server
```

### Проблема: Медленная транскрипция

```bash
# Проверка GPU
nvidia-smi

# Использование меньшей модели
# В .env: WILLOW_WHISPER_MODEL=whisper-base
```

### Проблема: Ошибки памяти

```bash
# Увеличение лимитов памяти
# В docker-compose.yml добавьте:
deploy:
  resources:
    limits:
      memory: 4G
```

## 📊 Производительность

### Оптимизация для разработки

```env
# В .env
WILLOW_WHISPER_MODEL=whisper-base
WILLOW_DEVICE=cpu
ENVIRONMENT=development
```

### Оптимизация для продакшена

```env
# В .env
WILLOW_WHISPER_MODEL=whisper-large-v3
WILLOW_DEVICE=cuda
ENVIRONMENT=production
MOUNT_CODE=ro
```

## 🎯 Заключение

Один `docker-compose.yml` файл покрывает все сценарии:

- ✅ **Разработка** - с hot reload и отладкой
- ✅ **Продакшен** - с оптимизацией и безопасностью  
- ✅ **Локальная разработка** - с внешним Willow
- ✅ **Гибкая конфигурация** - через переменные окружения

**Просто запустите:**
```bash
./start.sh dev
```

И все заработает! 🚀
