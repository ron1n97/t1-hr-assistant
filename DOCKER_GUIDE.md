# Docker Guide для T1 HR Assistant

Руководство по контейнеризации и развертыванию T1 HR Assistant с использованием Docker и Docker Compose.

## 🐳 Обзор

Проект полностью контейнеризован с использованием:
- **Docker** для создания образов
- **Docker Compose** для оркестрации
- **uv** для управления Python зависимостями
- **FastAPI** с Uvicorn для веб-сервера

## 📁 Docker файлы

### Dockerfile
- Основан на `python:3.12-slim`
- Устанавливает `uv` для быстрого управления пакетами
- Создает безопасного пользователя `app`
- Оптимизирован для продакшена

### docker-compose.yml
- Основной сервис `t1-hr-assistant`
- Health checks для мониторинга
- Volume для кэша uv
- Настраиваемая сеть

### .dockerignore
- Исключает ненужные файлы из контекста сборки
- Оптимизирует размер образа

## 🚀 Быстрый старт

### 1. Подготовка окружения

```bash
# Создайте .env файл
echo "SCIBOX_API_KEY=your_api_key_here" > .env
```

### 2. Сборка и запуск

```bash
# Используя скрипт (рекомендуется)
chmod +x docker-scripts.sh
./docker-scripts.sh build

# Или напрямую через docker-compose
docker-compose up --build -d
```

### 3. Проверка

```bash
# Проверка статуса
./docker-scripts.sh status

# Тестирование API
./docker-scripts.sh test

# Просмотр логов
./docker-scripts.sh logs
```

## 🛠️ Управление контейнерами

### Скрипт docker-scripts.sh

Удобный скрипт для управления контейнерами:

```bash
# Сборка и запуск (первый раз)
./docker-scripts.sh build

# Запуск
./docker-scripts.sh start

# Остановка
./docker-scripts.sh stop

# Перезапуск
./docker-scripts.sh restart

# Просмотр логов
./docker-scripts.sh logs

# Статус контейнеров
./docker-scripts.sh status

# Тестирование API
./docker-scripts.sh test

# Очистка ресурсов
./docker-scripts.sh clean

# Обновление
./docker-scripts.sh update
```

### Прямые команды Docker Compose

```bash
# Запуск в фоне
docker-compose up -d

# Запуск с пересборкой
docker-compose up --build -d

# Остановка
docker-compose down

# Просмотр логов
docker-compose logs -f

# Статус
docker-compose ps

# Выполнение команд в контейнере
docker-compose exec t1-hr-assistant bash
```

## 🔧 Конфигурация

### Переменные окружения

Основные переменные в `.env`:

```env
# Обязательные
SCIBOX_API_KEY=your_api_key_here

# Опциональные
PYTHONPATH=/app
UV_SYSTEM_PYTHON=1
```

### Порты

- **8000** - FastAPI сервер (основной)
- Можно добавить nginx на порты 80/443

### Volumes

- `/app` - монтирование кода (для разработки)
- `uv-cache` - кэш uv для ускорения сборки

## 📊 Мониторинг

### Health Checks

Автоматическая проверка здоровья:

```bash
# Проверка через API
curl http://localhost:8000/health

# Проверка через Docker
docker-compose ps
```

### Логи

```bash
# Просмотр логов
./docker-scripts.sh logs

# Логи с фильтрацией
docker-compose logs -f --tail=100 t1-hr-assistant

# Логи в реальном времени
docker-compose logs -f
```

## 🧪 Тестирование

### Автоматическое тестирование

```bash
# Полное тестирование
./docker-scripts.sh test

# Ручное тестирование
curl -X POST "http://localhost:8000/chat/hr" \
  -H "Content-Type: application/json" \
  -d '{"message": "Привет!"}'
```

### Тестирование в контейнере

```bash
# Вход в контейнер
docker-compose exec t1-hr-assistant bash

# Запуск тестов
uv run python test_api.py
```

## 🚀 Развертывание

### Локальная разработка

```bash
# Запуск с монтированием кода
docker-compose up --build -d

# Изменения в коде автоматически подхватываются
# (благодаря volume монтированию)
```

### Продакшен

1. **Удалите volume монтирование** из `docker-compose.yml`:
   ```yaml
   # Закомментируйте эту строку
   # - .:/app
   ```

2. **Соберите финальный образ**:
   ```bash
   docker-compose build --no-cache
   ```

3. **Запустите**:
   ```bash
   docker-compose up -d
   ```

### Docker Registry

```bash
# Тегирование образа
docker tag t1-hr-assistant:latest your-registry/t1-hr-assistant:latest

# Отправка в registry
docker push your-registry/t1-hr-assistant:latest
```

## 🔒 Безопасность

### Рекомендации для продакшена

1. **Используйте secrets** вместо .env:
   ```yaml
   secrets:
     - scibox_api_key
   ```

2. **Ограничьте ресурсы**:
   ```yaml
   deploy:
     resources:
       limits:
         memory: 512M
         cpus: '0.5'
   ```

3. **Используйте non-root пользователя** (уже настроено)

4. **Настройте nginx** для SSL и rate limiting

## 🐛 Отладка

### Проблемы с uv

Если возникают проблемы с установкой или использованием `uv`:

```bash
# Используйте альтернативный Dockerfile с pip
./docker-scripts.sh build pip

# Или напрямую через docker-compose
DOCKERFILE=Dockerfile.pip docker-compose up --build -d
```

**Основные проблемы с uv:**
- `exit code: 127` - uv не найден в PATH
- `--frozen` ошибки - проблемы с lock файлом
- Проблемы с установкой в контейнере

**Решение:** Используйте `Dockerfile.pip` для стабильной работы.

### Проблемы с запуском

```bash
# Проверка логов
docker-compose logs t1-hr-assistant

# Проверка переменных окружения
docker-compose exec t1-hr-assistant env

# Проверка файлов в контейнере
docker-compose exec t1-hr-assistant ls -la /app
```

### Проблемы с зависимостями

```bash
# Пересборка без кэша
docker-compose build --no-cache

# Очистка volumes
docker-compose down -v

# Если проблемы с uv, используйте pip версию
./docker-scripts.sh build pip
```

### Проблемы с сетью

```bash
# Проверка портов
docker-compose ps
netstat -tlnp | grep 8000

# Проверка сети
docker network ls
docker network inspect t1-hr-assistant_t1-hr-network
```

## 📈 Масштабирование

### Горизонтальное масштабирование

```yaml
# В docker-compose.yml
services:
  t1-hr-assistant:
    # ... конфигурация
    deploy:
      replicas: 3
```

### Load Balancer

Добавьте nginx для балансировки нагрузки:

```yaml
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
  depends_on:
    - t1-hr-assistant
```

## 🔄 CI/CD

### GitHub Actions пример

```yaml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy
        run: |
          docker-compose up --build -d
```

## 📝 Полезные команды

```bash
# Очистка всего Docker
docker system prune -a

# Просмотр использования ресурсов
docker stats

# Экспорт/импорт образов
docker save t1-hr-assistant:latest | gzip > t1-hr-assistant.tar.gz
docker load < t1-hr-assistant.tar.gz

# Backup volumes
docker run --rm -v t1-hr-assistant_uv-cache:/data -v $(pwd):/backup alpine tar czf /backup/uv-cache-backup.tar.gz -C /data .
```
