# 🚀 Быстрый старт T1 HR Assistant

## ⚡ За 3 минуты

### 1. Настройка
```bash
# Скопируйте конфигурацию
cp env.example .env

# Отредактируйте .env файл
# Укажите ваш SCIBOX_API_KEY
```

### 2. Запуск
```bash
# Один файл docker-compose.yml!
docker-compose up --build -d
```

### 3. Проверка
```bash
# API
curl http://localhost:8000/health

# Frontend
open http://localhost:3000

# Willow
curl http://localhost:8001/health
```

## 🎯 Готово!

**Сервисы доступны:**
- 🌐 **API:** http://localhost:8000
- 🎨 **Frontend:** http://localhost:3000  
- 🎤 **Willow:** http://localhost:8001

## 🔧 Управление

```bash
# Остановка
docker-compose down

# Логи
docker-compose logs -f

# Статус
docker-compose ps

# Перезапуск
docker-compose restart
```

## 🧪 Тестирование

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

## 📋 Альтернативные команды

### Через Makefile
```bash
make build    # Сборка и запуск
make stop     # Остановка
make logs     # Логи
make test     # Тестирование
make help     # Справка
```

### Через скрипт
```bash
./start.sh dev    # Разработка
./start.sh prod   # Продакшен
./start.sh local  # С локальным Willow
```

## ⚙️ Настройки

### Режимы работы
```bash
# Разработка (по умолчанию)
docker-compose up -d

# Продакшен
ENVIRONMENT=production MOUNT_CODE=ro docker-compose up -d

# С локальным Willow
WILLOW_SERVER_URL=http://host.docker.internal:8001 docker-compose up -d
```

### GPU поддержка
```bash
# В .env файле
WILLOW_DEVICE=cuda
```

### Разные модели Whisper
```bash
# В .env файле
WILLOW_WHISPER_MODEL=whisper-base      # Быстро
WILLOW_WHISPER_MODEL=whisper-medium    # Средне
WILLOW_WHISPER_MODEL=whisper-large-v3  # Точно (по умолчанию)
```

## 🎉 Готово к использованию!

Один `docker-compose.yml` файл покрывает все сценарии:
- ✅ Разработка с hot reload
- ✅ Продакшен с оптимизацией
- ✅ Локальная разработка с внешним Willow
- ✅ Гибкая конфигурация через переменные

**Просто запустите и все заработает!** 🚀
