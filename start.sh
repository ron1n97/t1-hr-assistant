#!/bin/bash

# Простой скрипт для запуска T1 HR Assistant с Willow

set -e

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Проверка .env файла
if [ ! -f .env ]; then
    warning ".env файл не найден, создаем из примера..."
    cp env.example .env
    warning "Отредактируйте .env файл с вашим API ключом!"
    exit 1
fi

# Параметры запуска
MODE=${1:-dev}
DOCKERFILE=${2:-Dockerfile}

case $MODE in
    "dev"|"development")
        log "Запуск в режиме разработки..."
        export ENVIRONMENT=development
        export MOUNT_CODE=z
        export WILLOW_SERVER_URL=http://willow-inference-server:8001
        ;;
    "prod"|"production")
        log "Запуск в режиме продакшена..."
        export ENVIRONMENT=production
        export MOUNT_CODE=ro
        export WILLOW_SERVER_URL=http://willow-inference-server:8001
        ;;
    "local")
        log "Запуск с локальным Willow сервером..."
        export ENVIRONMENT=development
        export MOUNT_CODE=z
        export WILLOW_SERVER_URL=http://host.docker.internal:8001
        warning "Убедитесь, что Willow запущен локально на порту 8001!"
        ;;
    *)
        error "Неизвестный режим: $MODE"
        echo "Использование: $0 [dev|prod|local] [Dockerfile]"
        echo "  dev    - Разработка с встроенным Willow"
        echo "  prod   - Продакшен с встроенным Willow"
        echo "  local  - Разработка с локальным Willow"
        exit 1
        ;;
esac

# Запуск Docker Compose
log "Запуск Docker Compose..."
docker-compose up --build -d

success "Сервисы запущены!"
echo ""
echo "🌐 API: http://localhost:8000"
echo "🎨 Frontend: http://localhost:3000"
echo "🎤 Willow: http://localhost:8001"
echo ""
echo "📊 Проверка статуса:"
echo "  docker-compose ps"
echo ""
echo "📋 Логи:"
echo "  docker-compose logs -f"
echo ""
echo "🧪 Тестирование:"
echo "  curl http://localhost:8000/health"
echo "  curl http://localhost:8001/health"
