.PHONY: help build up down logs restart clean backup restore init create-db

help:
	@echo "Доступные команды:"
	@echo "  make build      - Собрать образы с чистым кэшем"
	@echo "  make create-db  - Создать базу данных в существующем PostgreSQL контейнере"
	@echo "  make up         - Запустить сервисы"
	@echo "  make down       - Остановить сервисы"
	@echo "  make logs       - Показать логи всех сервисов"
	@echo "  make restart    - Перезапустить сервисы"
	@echo "  make clean      - Очистить все данные и volumes"
	@echo "  make backup     - Создать резервную копию БД"
	@echo "  make restore    - Восстановить БД из резервной копии"
	@echo "  make init       - Инициализировать базу данных"
	@echo "  make status     - Показать статус сервисов"
	@echo "  make health     - Проверить здоровье сервисов"

build:
	docker compose build --no-cache

create-db:
	@echo "Создание базы данных raffle_web3 в существующем PostgreSQL контейнере..."
	docker exec -it timecapsule_postgres psql -U postgres -c "CREATE DATABASE raffle_web3;" || echo "База данных уже существует"
	@echo "✅ База данных создана/проверена"

up:
	docker compose up -d
	@echo "✅ Сервисы запущены"
	@echo "Контейнеры используют внутреннюю сеть postgres_timecapsule_network"
	@echo "Подключение к существующим контейнерам: timecapsule_postgres и bg-remove-bot-redis-1"

down:
	docker compose down

logs:
	docker compose logs -f --tail=100

restart:
	docker compose restart

clean:
	docker compose down -v
	docker system prune -af

backup:
	@mkdir -p backups
	docker exec timecapsule_postgres pg_dump -U $${POSTGRES_USER:-postgres} $${POSTGRES_DB:-raffle_web3} > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "✅ Резервная копия создана в директории backups/"

restore:
	@if [ -z "$(FILE)" ]; then echo "Использование: make restore FILE=backups/backup_YYYYMMDD_HHMMSS.sql"; exit 1; fi
	docker exec -i timecapsule_postgres psql -U $${POSTGRES_USER:-postgres} $${POSTGRES_DB:-raffle_web3} < $(FILE)
	@echo "✅ База данных восстановлена из $(FILE)"

init:
	docker compose exec backend alembic upgrade head
	docker compose exec backend python -m app.scripts.init_raffles
	@echo "✅ База данных инициализирована"

status:
	@echo "Статус сервисов:"
	docker compose ps

health:
	@echo "Проверка здоровья сервисов:"
	@docker compose ps --format "table {{.Service}}\t{{.Status}}\t{{.Ports}}"
