#!/bin/bash

# Скрипт для управления Docker контейнерами T1 HR Assistant

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка наличия .env файла
check_env() {
    if [ ! -f .env ]; then
        error ".env файл не найден!"
        log "Создайте .env файл с переменной SCIBOX_API_KEY"
        echo "SCIBOX_API_KEY=your_api_key_here" > .env
        warning "Создан пример .env файла. Отредактируйте его с вашим API ключом."
        exit 1
    fi
}

# Сборка и запуск
build_and_run() {
    log "Сборка и запуск T1 HR Assistant с Willow Inference Server..."
    check_env
    
    # Проверяем, какой режим использовать
    if [ "$2" = "prod" ]; then
        log "Запуск в продакшен режиме с встроенным Willow"
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
    elif [ "$2" = "pip" ]; then
        log "Используется Dockerfile с pip"
        DOCKERFILE=Dockerfile.pip docker-compose up --build -d
    else
        log "Используется Dockerfile с uv (разработка)"
        docker-compose up --build -d
    fi
    
    success "Сервис запущен!"
    log "API доступен по адресу: http://localhost:8000"
    log "Willow Inference Server: http://localhost:8001"
    log "Документация: http://localhost:8000/docs"
    log "Проверка здоровья: http://localhost:8000/health"
    log "Проверка Willow: http://localhost:8001/health"
}

# Запуск
start() {
    log "Запуск T1 HR Assistant..."
    check_env
    
    docker-compose up -d
    
    success "Сервис запущен!"
    log "API доступен по адресу: http://localhost:8000"
}

# Остановка
stop() {
    log "Остановка T1 HR Assistant..."
    docker-compose down
    success "Сервис остановлен!"
}

# Перезапуск
restart() {
    log "Перезапуск T1 HR Assistant..."
    docker-compose restart
    success "Сервис перезапущен!"
}

# Просмотр логов
logs() {
    log "Просмотр логов T1 HR Assistant..."
    docker-compose logs -f
}

# Статус
status() {
    log "Статус контейнеров:"
    docker-compose ps
}

# Очистка
clean() {
    log "Очистка Docker ресурсов..."
    docker-compose down -v --remove-orphans
    docker system prune -f
    success "Очистка завершена!"
}

# Тестирование
test() {
    log "Тестирование API..."
    
    # Ждем запуска сервиса
    log "Ожидание запуска сервиса..."
    sleep 10
    
    # Проверка здоровья основного сервиса
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        success "Основной сервис здоров!"
        
        # Проверка Willow сервера
        if curl -f http://localhost:8001/health > /dev/null 2>&1; then
            success "Willow Inference Server работает!"
        else
            warning "Willow Inference Server недоступен (возможно, используется локальный)"
        fi
        
        # Тест HR агента
        log "Тестирование HR агента..."
        response=$(curl -s -X POST "http://localhost:8000/chat/hr" \
            -H "Content-Type: application/json" \
            -d '{"message": "Привет!"}')
        
        if echo "$response" | grep -q "response"; then
            success "HR агент работает!"
        else
            error "HR агент не отвечает"
        fi
        
        # Тест User агента
        log "Тестирование User агента..."
        response=$(curl -s -X POST "http://localhost:8000/chat/user" \
            -H "Content-Type: application/json" \
            -d '{"message": "Привет!"}')
        
        if echo "$response" | grep -q "response"; then
            success "User агент работает!"
        else
            error "User агент не отвечает"
        fi
        
        # Тест транскрипции (если Willow доступен)
        if curl -f http://localhost:8001/health > /dev/null 2>&1; then
            log "Тестирование транскрипции аудио..."
            # Создаем тестовый аудио файл (заглушка)
            echo "Тест транскрипции" > /tmp/test_audio.txt
            response=$(curl -s -X POST "http://localhost:8000/audio/transcriptions" \
                -F "file=@/tmp/test_audio.txt" \
                -F "agent_type=user" \
                -F "conversation_id=test123" 2>/dev/null || echo "Ошибка транскрипции")
            
            if echo "$response" | grep -q "text"; then
                success "Транскрипция работает!"
            else
                warning "Транскрипция недоступна (требуется реальный аудио файл)"
            fi
            rm -f /tmp/test_audio.txt
        fi
        
    else
        error "Основной сервис недоступен!"
    fi
}

# Обновление
update() {
    log "Обновление T1 HR Assistant..."
    docker-compose pull
    docker-compose up --build -d
    success "Обновление завершено!"
}

# Помощь
help() {
    echo "T1 HR Assistant Docker Management Script"
    echo ""
    echo "Использование: $0 [команда]"
    echo ""
    echo "Команды:"
    echo "  build     - Сборка и запуск (с пересборкой)"
    echo "  start     - Запуск сервиса"
    echo "  stop      - Остановка сервиса"
    echo "  restart   - Перезапуск сервиса"
    echo "  logs      - Просмотр логов"
    echo "  status    - Статус контейнеров"
    echo "  test      - Тестирование API"
    echo "  clean     - Очистка Docker ресурсов"
    echo "  update    - Обновление сервиса"
    echo "  help      - Показать эту справку"
    echo ""
    echo "Примеры:"
    echo "  $0 build       # Разработка с локальным Willow"
    echo "  $0 build prod  # Продакшен с встроенным Willow"
    echo "  $0 build pip   # Разработка с pip"
    echo "  $0 logs        # Просмотр логов"
    echo "  $0 test        # Тестирование всех сервисов"
}

# Основная логика
case "${1:-help}" in
    build)
        build_and_run
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        logs
        ;;
    status)
        status
        ;;
    test)
        test
        ;;
    clean)
        clean
        ;;
    update)
        update
        ;;
    help|--help|-h)
        help
        ;;
    *)
        error "Неизвестная команда: $1"
        help
        exit 1
        ;;
esac
