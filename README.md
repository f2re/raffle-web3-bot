# Web3 Raffle Telegram Mini App

> Автоматизированное Web3 приложение для проведения провабельно честных розыгрышей в Telegram с интеграцией TON кошелька.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node](https://img.shields.io/badge/node-20+-green.svg)](https://nodejs.org/)
[![Docker](https://img.shields.io/badge/docker-compose-blue.svg)](https://docs.docker.com/compose/)

## 📑 Документация

- **[SETUP.md](SETUP.md)** - Полное руководство по установке и запуску (Docker и без Docker)
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Руководство для разработчиков
- **[API Documentation](http://localhost:8000/docs)** - OpenAPI/Swagger документация (после запуска)

## ✨ Особенности

- 🎯 **3 типа розыгрышей**: Express (1 TON), Standard (2 TON), Premium (5 TON)
- 🔐 **Провабельно честно**: Использует Random.org API для генерации победителя
- 💎 **TON Blockchain**: Полная интеграция с TON для приема и отправки платежей
- 🤖 **Telegram Bot**: Интеграция с Telegram Mini App
- ⚡ **Автоматизация**: Автоматический запуск розыгрышей и выплата призов
- 📊 **Real-time обновления**: WebSocket для live-обновлений
- 🔒 **Безопасность**: Проверка Telegram WebApp auth, валидация транзакций, rate limiting
- 📦 **Docker**: Полная контейнеризация для простого развертывания

## 🛠 Технологический стек

### Backend
- **Python 3.11+** - Основной язык
- **FastAPI** - Современный, быстрый веб-фреймворк
- **aiogram 3.x** - Telegram Bot framework
- **PostgreSQL 14+** - Основная база данных
- **Redis 7+** - Кэш и очереди
- **SQLAlchemy 2.0** - Async ORM
- **Alembic** - Миграции базы данных
- **APScheduler** - Планировщик задач
- **pytoniq** - TON blockchain интеграция

### Frontend
- **Vue.js 3.4+** - Progressive JavaScript framework
- **TypeScript 5.6+** - Type safety
- **Vite 5.4+** - Next generation build tool
- **Pinia** - State management
- **TailwindCSS** - Utility-first CSS
- **@tonconnect/ui-vue** - TON wallet integration
- **axios** - HTTP client

### Infrastructure
- **Docker** - Контейнеризация
- **Docker Compose** - Оркестрация сервисов
- **Nginx** - Reverse proxy (production)

## 🚀 Быстрый старт

### Требования

#### С Docker (рекомендуется):
- Docker 20.10+
- Docker Compose v2
- Git
- 2GB+ RAM
- 10GB+ свободного места

#### Без Docker:
- Python 3.11+
- Node.js 20+
- PostgreSQL 14+
- Redis 7+
- Git

### Установка с Docker

1. **Клонировать репозиторий**:
```bash
git clone https://github.com/f2re/raffle-web3-bot.git
cd raffle-web3-bot
```

2. **Создать .env файл**:
```bash
cp .env.example .env
```

3. **Настроить .env** - Заполнить обязательные параметры:
```env
# PostgreSQL
POSTGRES_PASSWORD=your_strong_password

# Redis
REDIS_PASSWORD=your_redis_password

# Backend
SECRET_KEY=your_secret_key_min_32_characters

# Telegram (получить у @BotFather)
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_USER_ID=123456789

# TON Blockchain (получить на toncenter.com)
RAFFLE_WALLET_ADDRESS=UQxxxx...
RAFFLE_WALLET_MNEMONIC=word1 word2 ... word24
TON_CENTER_API_KEY=your_toncenter_api_key

# Random.org (получить на random.org)
RANDOM_ORG_API_KEY=your_random_org_api_key

# Frontend
VITE_API_URL=https://your-backend.com/api/v1
VITE_WS_URL=wss://your-backend.com/ws
```

4. **Собрать и запустить**:
```bash
# Собрать образы
make build

# Запустить все сервисы
make up

# Проверить статус
make status
```

5. **Инициализировать базу данных**:
```bash
make init
```

6. **Проверить работу**:
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

### Установка без Docker

Смотрите подробные инструкции в **[SETUP.md](SETUP.md#запуск-без-docker)**

## 📋 Команды управления (Makefile)

```bash
make help       # Показать все доступные команды
make build      # Собрать Docker образы с чистым кэшем
make up         # Запустить все сервисы
make down       # Остановить все сервисы
make logs       # Показать логи всех сервисов
make restart    # Перезапустить сервисы
make status     # Показать статус сервисов
make health     # Проверить здоровье сервисов
make clean      # Очистить все данные и volumes
make backup     # Создать резервную копию БД
make restore    # Восстановить БД из резервной копии
make init       # Инициализировать базу данных
```

## Структура проекта

```
raffle-web3-bot/
├── backend/              # Python backend
│   ├── app/
│   │   ├── api/          # FastAPI routes & auth
│   │   ├── bot/          # Telegram bot handlers
│   │   ├── database/     # SQLAlchemy models & CRUD
│   │   ├── services/     # Business logic
│   │   ├── schemas/      # Pydantic schemas
│   │   └── main.py       # Application entry point
│   ├── alembic/          # Database migrations
│   └── requirements.txt  # Python dependencies
│
├── frontend/             # Vue.js frontend
│   ├── src/
│   │   ├── components/   # Vue components
│   │   ├── views/        # Page views
│   │   ├── stores/       # Pinia stores
│   │   ├── api/          # API client
│   │   └── types/        # TypeScript types
│   └── package.json      # Node dependencies
│
├── docker-compose.yml    # Docker orchestration
├── .env.example          # Environment variables template
└── Makefile              # Management commands
```

## Типы розыгрышей

### Express (Экспресс)
- Минимум участников: 5
- Взнос: 1 TON
- Приз: 4.5 TON (10% комиссия)
- Таймер: 1 минута

### Standard (Стандарт)
- Минимум участников: 10
- Взнос: 2 TON
- Приз: 18 TON (10% комиссия)
- Таймер: 2 минуты

### Premium (Премиум)
- Минимум участников: 30
- Взнос: 5 TON
- Приз: 135 TON (10% комиссия)
- Таймер: 5 минут

## Жизненный цикл розыгрыша

1. **Создание**: Автоматически создается новый розыгрыш каждого типа
2. **Набор участников**: Пользователи присоединяются через TON Connect
3. **Ожидание**: После достижения минимума участников запускается таймер
4. **Розыгрыш**: По истечении таймера вызывается Random.org API
5. **Выплата**: Приз автоматически отправляется победителю
6. **Новый розыгрыш**: Создается следующий розыгрыш того же типа

## API Endpoints

### Raffles
- `GET /api/v1/raffles/active` - Получить активные розыгрыши
- `GET /api/v1/raffles/{id}` - Получить детали розыгрыша
- `POST /api/v1/raffles/{id}/join` - Присоединиться к розыгрышу

### User
- `GET /api/v1/user/stats` - Получить статистику пользователя
- `GET /api/v1/history` - Получить историю розыгрышей

### WebSocket
- `WS /ws` - Real-time обновления розыгрышей

## Настройка Telegram Bot

1. Создать бота через @BotFather:
```
/newbot
```

2. Настроить команды:
```
/setcommands
start - Запустить бота
help - Помощь
```

3. Создать Mini App:
```
/newapp
```

4. Настроить Menu Button:
```
/setmenubutton
```

## Безопасность

- ✅ Проверка Telegram WebApp auth
- ✅ Валидация блокчейн транзакций
- ✅ Идемпотентность транзакций
- ✅ Rate limiting
- ✅ CORS защита
- ✅ Все пароли через .env
- ✅ Провабельно честный розыгрыш (Random.org)

## 💻 Разработка

Подробное руководство по разработке смотрите в **[DEVELOPMENT.md](DEVELOPMENT.md)**

### Quick start для разработки

#### Backend:
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend:
```bash
cd frontend
npm install
npm run dev
```

## 🚢 Деплой в production

### С Docker Compose

1. Настроить production .env файл
2. Настроить SSL сертификаты в `nginx/ssl/`
3. Создать `nginx/nginx.conf` для production
4. Запустить с production профилем:

```bash
# Собрать production образы
make build

# Запустить с nginx reverse proxy
docker compose --profile production up -d

# Проверить статус
make health
```

### Переменные окружения для production

```env
ENVIRONMENT=production
LOG_LEVEL=INFO

# Использовать HTTPS URLs
VITE_API_URL=https://your-domain.com/api/v1
VITE_WS_URL=wss://your-domain.com/ws

# Настроить CORS
CORS_ORIGINS=https://your-miniapp-domain.com,https://your-production-domain.com

# Использовать сильные пароли
POSTGRES_PASSWORD=<strong-random-password>
REDIS_PASSWORD=<strong-random-password>
SECRET_KEY=<strong-random-secret-min-32-chars>
```

## 🔧 Устранение неполадок

### Ошибка сборки frontend (vue-tsc)

**Проблема**: `Search string not found: "/supportedTSExtensions = .*(?=;)/"`

**Решение**: Обновлены версии в `frontend/package.json`:
```json
{
  "devDependencies": {
    "vue-tsc": "^2.1.10",
    "typescript": "^5.6.3",
    "vite": "^5.4.11"
  }
}
```

### Redis healthcheck fails

**Проблема**: Redis healthcheck не проходит

**Решение**: Исправлена команда healthcheck в `docker-compose.yml`:
```yaml
healthcheck:
  test: ["CMD", "redis-cli", "--no-auth-warning", "-a", "${REDIS_PASSWORD:-redis}", "ping"]
```

### Docker compose version warning

**Проблема**: `WARN[0000] the attribute 'version' is obsolete`

**Решение**: Удалена строка `version: '3.8'` из `docker-compose.yml`

Больше решений проблем смотрите в **[SETUP.md](SETUP.md#устранение-неполадок)**

