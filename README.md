# Web3 Raffle Telegram Mini App

Автоматизированное Web3 приложение для проведения провабельно честных розыгрышей в Telegram с интеграцией TON кошелька.

## Особенности

- 🎯 **3 типа розыгрышей**: Express (1 TON), Standard (2 TON), Premium (5 TON)
- 🔐 **Провабельно честно**: Использует Random.org API для генерации победителя
- 💎 **TON Blockchain**: Полная интеграция с TON для приема и отправки платежей
- 🤖 **Telegram Bot**: Интеграция с Telegram Mini App
- ⚡ **Автоматизация**: Автоматический запуск розыгрышей и выплата призов
- 📊 **Real-time обновления**: WebSocket для live-обновлений

## Технологический стек

### Backend
- Python 3.11+
- FastAPI (REST API)
- aiogram 3.x (Telegram Bot)
- PostgreSQL 14+ (база данных)
- Redis 6+ (кэш)
- SQLAlchemy 2.0 (ORM)
- APScheduler (планировщик задач)
- pytoniq (TON blockchain)

### Frontend
- Vue.js 3.4+ с TypeScript
- Vite (сборка)
- Pinia (управление состоянием)
- TailwindCSS (стилизация)
- @tonconnect/ui-vue (TON кошельки)
- @telegram-apps/sdk-vue (Telegram интеграция)

## Быстрый старт

### Требования

- Docker & Docker Compose
- Node.js 20+ (для локальной разработки)
- Python 3.11+ (для локальной разработки)

### Установка

1. Клонировать репозиторий:
```bash
git clone https://github.com/f2re/raffle-web3-bot.git
cd raffle-web3-bot
```

2. Создать .env файл:
```bash
cp .env.example .env
```

3. Заполнить конфигурацию в .env:
```env
# PostgreSQL
POSTGRES_PASSWORD=your_strong_password

# Redis
REDIS_PASSWORD=your_redis_password

# Backend
SECRET_KEY=your_secret_key_32_chars_min

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather

# TON Blockchain
RAFFLE_WALLET_ADDRESS=your_ton_wallet_address
RAFFLE_WALLET_MNEMONIC=your 24 word mnemonic
TON_CENTER_API_KEY=your_toncenter_api_key

# Random.org
RANDOM_ORG_API_KEY=your_random_org_api_key

# Frontend
VITE_API_URL=https://your-backend-url.com/api/v1
VITE_WS_URL=wss://your-backend-url.com/ws
```

4. Запустить с Docker Compose:
```bash
make up
# или
docker-compose up -d
```

5. Инициализировать базу данных:
```bash
make init
# или
docker-compose exec backend python -m app.scripts.init_raffles
```

## Команды Makefile

```bash
make help       # Показать все доступные команды
make build      # Собрать Docker образы
make up         # Запустить все сервисы
make down       # Остановить все сервисы
make logs       # Показать логи
make restart    # Перезапустить сервисы
make clean      # Очистить все данные
make backup     # Создать резервную копию БД
make init       # Инициализировать БД
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

## Разработка

### Backend development
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

### Frontend development
```bash
cd frontend
npm install
npm run dev
```

## Деплой в production

1. Настроить .env с production значениями
2. Настроить SSL сертификаты
3. Запустить с production профилем:
```bash
docker-compose --profile production up -d
```

