.PHONY: help build up down logs restart clean backup restore init

help:
	@echo "Доступные команды:"
	@echo "  make build    - Собрать образы"
	@echo "  make up       - Запустить сервисы"
	@echo "  make down     - Остановить сервисы"
	@echo "  make logs     - Показать логи"
	@echo "  make restart  - Перезапустить"
	@echo "  make clean    - Очистить данные"
	@echo "  make backup   - Резервная копия БД"
	@echo "  make init     - Инициализировать БД"

build:
	docker-compose build --no-cache

up:
	docker-compose up -d
	@echo "✅ Сервисы запущены"
	@echo "Backend: http://localhost:$${BACKEND_PORT:-8000}"
	@echo "Frontend: http://localhost:$${FRONTEND_PORT:-3000}"

down:
	docker-compose down

logs:
	docker-compose logs -f --tail=100

restart:
	docker-compose restart

clean:
	docker-compose down -v
	docker system prune -af

backup:
	docker-compose exec postgres pg_dump -U postgres raffle_web3 > backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "✅ Резервная копия создана"

init:
	docker-compose exec backend alembic upgrade head
	docker-compose exec backend python -m app.scripts.init_raffles
	@echo "✅ База данных инициализирована"
