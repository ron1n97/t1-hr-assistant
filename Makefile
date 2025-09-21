# T1 HR Assistant Makefile

.PHONY: help build start stop restart logs status test clean dev prod local

# Цвета
BLUE = \033[0;34m
GREEN = \033[0;32m
YELLOW = \033[1;33m
NC = \033[0m

help: ## Показать справку
	@echo "$(BLUE)T1 HR Assistant - Управление через Makefile$(NC)"
	@echo ""
	@echo "Доступные команды:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Сборка и запуск (разработка)
	@echo "$(BLUE)Сборка и запуск в режиме разработки...$(NC)"
	docker-compose up --build -d

start: ## Запуск сервисов
	@echo "$(BLUE)Запуск сервисов...$(NC)"
	docker-compose up -d

stop: ## Остановка сервисов
	@echo "$(BLUE)Остановка сервисов...$(NC)"
	docker-compose down

restart: ## Перезапуск сервисов
	@echo "$(BLUE)Перезапуск сервисов...$(NC)"
	docker-compose restart

logs: ## Просмотр логов
	@echo "$(BLUE)Просмотр логов...$(NC)"
	docker-compose logs -f

status: ## Статус сервисов
	@echo "$(BLUE)Статус сервисов:$(NC)"
	docker-compose ps

test: ## Тестирование API
	@echo "$(BLUE)Тестирование API...$(NC)"
	@echo "Проверка API..."
	@curl -s http://localhost:8000/health > /dev/null && echo "$(GREEN)✅ API работает$(NC)" || echo "$(YELLOW)❌ API недоступен$(NC)"
	@echo "Проверка Willow..."
	@curl -s http://localhost:8001/health > /dev/null && echo "$(GREEN)✅ Willow работает$(NC)" || echo "$(YELLOW)❌ Willow недоступен$(NC)"

clean: ## Очистка Docker ресурсов
	@echo "$(BLUE)Очистка Docker ресурсов...$(NC)"
	docker-compose down -v --remove-orphans
	docker system prune -f

dev: ## Запуск в режиме разработки
	@echo "$(BLUE)Запуск в режиме разработки...$(NC)"
	ENVIRONMENT=development MOUNT_CODE=z docker-compose up --build -d

prod: ## Запуск в режиме продакшена
	@echo "$(BLUE)Запуск в режиме продакшена...$(NC)"
	ENVIRONMENT=production MOUNT_CODE=ro docker-compose up --build -d

local: ## Запуск с локальным Willow
	@echo "$(BLUE)Запуск с локальным Willow...$(NC)"
	@echo "$(YELLOW)Убедитесь, что Willow запущен локально на порту 8001!$(NC)"
	WILLOW_SERVER_URL=http://host.docker.internal:8001 ENVIRONMENT=development MOUNT_CODE=z docker-compose up --build -d

# Алиасы
up: build
down: stop
ps: status
