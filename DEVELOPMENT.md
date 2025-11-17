# Руководство по разработке Web3 Raffle Bot

## Оглавление

1. [Настройка среды разработки](#настройка-среды-разработки)
2. [Архитектура проекта](#архитектура-проекта)
3. [Backend разработка](#backend-разработка)
4. [Frontend разработка](#frontend-разработка)
5. [База данных и миграции](#база-данных-и-миграции)
6. [Тестирование](#тестирование)
7. [Стандарты кода](#стандарты-кода)
8. [Git workflow](#git-workflow)

---

## Настройка среды разработки

### Требования

- Python 3.11+
- Node.js 20+
- PostgreSQL 14+
- Redis 7+
- Git
- VS Code или PyCharm (рекомендуется)

### Рекомендуемые VS Code расширения

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "Vue.volar",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "ms-azuretools.vscode-docker",
    "bradlc.vscode-tailwindcss"
  ]
}
```

### Настройка backend для разработки

```bash
# Клонировать репозиторий
git clone https://github.com/f2re/raffle-web3-bot.git
cd raffle-web3-bot

# Перейти в директорию backend
cd backend

# Создать виртуальное окружение
python3.11 -m venv venv

# Активировать виртуальное окружение
source venv/bin/activate  # Linux/macOS
# или
.\venv\Scripts\activate  # Windows

# Обновить pip
pip install --upgrade pip

# Установить зависимости для разработки
pip install -r requirements.txt
pip install -r requirements-dev.txt  # если есть
```

### Настройка frontend для разработки

```bash
# Перейти в директорию frontend
cd frontend

# Установить зависимости
npm install

# Создать .env.local файл для локальной разработки
cat > .env.local << EOF
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
VITE_RAFFLE_WALLET=EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c
VITE_TON_MANIFEST_URL=http://localhost:5173/tonconnect-manifest.json
EOF
```

### Настройка базы данных для разработки

```bash
# Создать базу данных PostgreSQL
createdb raffle_web3_dev

# Настроить .env файл в корне проекта
cat > .env << EOF
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/raffle_web3_dev
REDIS_URL=redis://:redis@localhost:6379/0
SECRET_KEY=development_secret_key_change_in_production
TELEGRAM_BOT_TOKEN=your_dev_bot_token
ADMIN_USER_ID=your_telegram_id
RAFFLE_WALLET_ADDRESS=test_wallet_address
RAFFLE_WALLET_MNEMONIC=test mnemonic phrase
TON_CENTER_API_KEY=test_api_key
RANDOM_ORG_API_KEY=test_random_api_key
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
EOF

# Выполнить миграции
cd backend
alembic upgrade head
```

---

## Архитектура проекта

### Общая структура

```
raffle-web3-bot/
├── backend/                    # Python backend (FastAPI + aiogram)
│   ├── alembic/                # Database migrations
│   │   ├── versions/           # Migration files
│   │   └── env.py              # Alembic environment config
│   ├── app/
│   │   ├── api/                # REST API endpoints
│   │   │   ├── auth.py         # Telegram WebApp authentication
│   │   │   ├── routes.py       # API routes (raffles, users, etc.)
│   │   │   └── websocket.py    # WebSocket connections
│   │   ├── bot/                # Telegram bot
│   │   │   ├── handlers/       # Message handlers
│   │   │   └── keyboards/      # Inline keyboards
│   │   ├── database/           # Database layer
│   │   │   ├── models.py       # SQLAlchemy models
│   │   │   ├── crud.py         # CRUD operations
│   │   │   └── session.py      # DB session management
│   │   ├── schemas/            # Pydantic schemas
│   │   │   └── pydantic.py     # Request/Response models
│   │   ├── services/           # Business logic
│   │   │   ├── raffle_service.py       # Raffle management
│   │   │   ├── ton_service.py          # TON blockchain integration
│   │   │   ├── random_service.py       # Random.org integration
│   │   │   └── scheduler_service.py    # APScheduler tasks
│   │   ├── scripts/            # Utility scripts
│   │   │   └── init_raffles.py # Initialize raffles
│   │   ├── config.py           # Application configuration
│   │   └── main.py             # Application entry point
│   └── requirements.txt        # Python dependencies
│
├── frontend/                   # Vue.js frontend
│   ├── src/
│   │   ├── api/                # API client
│   │   │   └── client.ts       # Axios instance and API calls
│   │   ├── components/         # Vue components
│   │   │   └── RaffleCard.vue  # Raffle display component
│   │   ├── router/             # Vue Router
│   │   │   └── index.ts        # Route definitions
│   │   ├── stores/             # Pinia stores
│   │   │   ├── raffle.ts       # Raffle state management
│   │   │   ├── user.ts         # User state management
│   │   │   └── wallet.ts       # TON wallet state
│   │   ├── styles/             # Global styles
│   │   │   └── main.css        # Tailwind CSS
│   │   ├── types/              # TypeScript types
│   │   │   └── index.ts        # Type definitions
│   │   ├── views/              # Page views
│   │   │   └── HomeView.vue    # Main page
│   │   ├── App.vue             # Root component
│   │   └── main.ts             # Application entry point
│   ├── package.json            # Node dependencies
│   ├── tsconfig.json           # TypeScript config
│   ├── vite.config.ts          # Vite config
│   └── tailwind.config.js      # Tailwind config
│
├── docker-compose.yml          # Docker orchestration
├── .env.example                # Environment variables template
├── Makefile                    # Management commands
├── README.md                   # Project overview
├── SETUP.md                    # Detailed setup guide
└── DEVELOPMENT.md              # This file
```

### Backend архитектура

Backend построен на **FastAPI** с использованием следующих паттернов:

1. **Layered Architecture**:
   - **API Layer** (`app/api/`): HTTP endpoints и WebSocket
   - **Service Layer** (`app/services/`): Business logic
   - **Data Layer** (`app/database/`): Database access
   - **Bot Layer** (`app/bot/`): Telegram bot handlers

2. **Dependency Injection**: FastAPI's dependency injection для DB sessions, auth, etc.

3. **Async/Await**: Полностью асинхронный код для высокой производительности

4. **Type Safety**: Pydantic models для валидации данных

### Frontend архитектура

Frontend построен на **Vue.js 3** с:

1. **Composition API**: Современный подход к компонентам
2. **Pinia**: State management
3. **TypeScript**: Type safety
4. **Tailwind CSS**: Utility-first CSS
5. **Vite**: Fast build tool

---

## Backend разработка

### Запуск backend в режиме разработки

```bash
cd backend
source venv/bin/activate

# С автоматической перезагрузкой при изменениях
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# С логами debug уровня
LOG_LEVEL=DEBUG uvicorn app.main:app --reload
```

### Структура API endpoints

#### Raffles
```python
GET  /api/v1/raffles/active      # Получить активные розыгрыши
GET  /api/v1/raffles/{id}        # Получить розыгрыш по ID
POST /api/v1/raffles/{id}/join   # Присоединиться к розыгрышу
GET  /api/v1/raffles/{id}/participants  # Получить участников
```

#### User
```python
GET  /api/v1/user/stats          # Статистика пользователя
GET  /api/v1/user/history        # История розыгрышей
```

#### Health
```python
GET  /api/v1/health              # Health check endpoint
```

#### WebSocket
```python
WS   /ws                         # WebSocket connection для real-time обновлений
```

### Добавление нового API endpoint

1. Создать Pydantic схему в `app/schemas/pydantic.py`:

```python
class NewFeatureRequest(BaseModel):
    field1: str
    field2: int

class NewFeatureResponse(BaseModel):
    id: int
    result: str
```

2. Добавить CRUD операции в `app/database/crud.py`:

```python
async def create_new_feature(db: AsyncSession, data: NewFeatureRequest):
    # Implementation
    pass
```

3. Создать бизнес-логику в `app/services/`:

```python
class NewFeatureService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def process(self, data: NewFeatureRequest):
        # Business logic
        pass
```

4. Добавить endpoint в `app/api/routes.py`:

```python
@router.post("/new-feature", response_model=NewFeatureResponse)
async def create_new_feature(
    request: NewFeatureRequest,
    db: AsyncSession = Depends(get_db)
):
    service = NewFeatureService(db)
    result = await service.process(request)
    return result
```

### Работа с базой данных

#### Создание новой модели

1. Добавить модель в `app/database/models.py`:

```python
class NewModel(Base):
    __tablename__ = "new_models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
```

2. Создать миграцию:

```bash
cd backend
alembic revision --autogenerate -m "Add new_models table"
```

3. Проверить сгенерированную миграцию в `alembic/versions/`

4. Применить миграцию:

```bash
alembic upgrade head
```

#### Откат миграции

```bash
# Откатить последнюю миграцию
alembic downgrade -1

# Откатить к конкретной версии
alembic downgrade <revision_id>

# Откатить все миграции
alembic downgrade base
```

### Работа с TON Blockchain

Сервис TON находится в `app/services/ton_service.py`:

```python
class TONService:
    async def check_transaction(self, tx_hash: str) -> bool:
        """Проверить транзакцию в блокчейне"""
        pass

    async def send_prize(self, address: str, amount: float):
        """Отправить приз победителю"""
        pass
```

### Работа с Telegram Bot

Хэндлеры бота находятся в `app/bot/handlers/`:

```python
# app/bot/handlers/custom.py
from aiogram import Router
from aiogram.types import Message

router = Router()

@router.message(Command("custom"))
async def custom_handler(message: Message):
    await message.answer("Custom response")
```

Не забудьте зарегистрировать router в `app/bot/__init__.py`.

### WebSocket для real-time обновлений

```python
# Отправить обновление всем подключенным клиентам
from app.api.websocket import manager

await manager.broadcast({
    "type": "raffle_updated",
    "data": raffle_data
})
```

---

## Frontend разработка

### Запуск frontend в режиме разработки

```bash
cd frontend
npm run dev

# Frontend будет доступен на http://localhost:5173
```

### Структура компонентов

```
src/
├── components/
│   ├── RaffleCard.vue      # Карточка розыгрыша
│   ├── ParticipantList.vue # Список участников
│   └── WalletButton.vue    # Кнопка подключения кошелька
├── views/
│   ├── HomeView.vue        # Главная страница
│   ├── RaffleView.vue      # Страница розыгрыша
│   └── HistoryView.vue     # История
└── stores/
    ├── raffle.ts           # Состояние розыгрышей
    ├── user.ts             # Состояние пользователя
    └── wallet.ts           # Состояние кошелька
```

### Создание нового компонента

```vue
<!-- src/components/NewComponent.vue -->
<template>
  <div class="new-component">
    <h2>{{ title }}</h2>
    <p>{{ content }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  title: string
  content: string
}

const props = defineProps<Props>()

const isActive = ref(false)

const toggleActive = () => {
  isActive.value = !isActive.value
}
</script>

<style scoped>
.new-component {
  @apply p-4 rounded-lg bg-white shadow;
}
</style>
```

### Работа с Pinia Store

```typescript
// src/stores/custom.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useCustomStore = defineStore('custom', () => {
  // State
  const items = ref<Item[]>([])
  const loading = ref(false)

  // Getters
  const itemCount = computed(() => items.value.length)

  // Actions
  async function fetchItems() {
    loading.value = true
    try {
      const response = await api.get('/items')
      items.value = response.data
    } catch (error) {
      console.error('Failed to fetch items:', error)
    } finally {
      loading.value = false
    }
  }

  return {
    items,
    loading,
    itemCount,
    fetchItems
  }
})
```

### API клиент

Все API вызовы централизованы в `src/api/client.ts`:

```typescript
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 10000
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Добавить auth token если есть
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Обработка ошибок
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default api
```

### WebSocket клиент

```typescript
// src/api/websocket.ts
class WebSocketClient {
  private ws: WebSocket | null = null

  connect() {
    this.ws = new WebSocket(import.meta.env.VITE_WS_URL)

    this.ws.onopen = () => {
      console.log('WebSocket connected')
    }

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      // Обработка сообщений
      this.handleMessage(data)
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    this.ws.onclose = () => {
      console.log('WebSocket closed')
      // Переподключение через 5 секунд
      setTimeout(() => this.connect(), 5000)
    }
  }

  private handleMessage(data: any) {
    // Обновить store на основе типа сообщения
    switch (data.type) {
      case 'raffle_updated':
        // Обновить раffle store
        break
      // ... другие типы
    }
  }

  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
    }
  }
}

export const wsClient = new WebSocketClient()
```

### Интеграция с TON Connect

```typescript
// src/stores/wallet.ts
import { TonConnectUI } from '@tonconnect/ui'

export const useWalletStore = defineStore('wallet', () => {
  const tonConnectUI = new TonConnectUI({
    manifestUrl: import.meta.env.VITE_TON_MANIFEST_URL
  })

  const walletAddress = ref<string | null>(null)
  const isConnected = computed(() => !!walletAddress.value)

  async function connect() {
    const wallet = await tonConnectUI.connectWallet()
    walletAddress.value = wallet.account.address
  }

  async function disconnect() {
    await tonConnectUI.disconnect()
    walletAddress.value = null
  }

  return {
    walletAddress,
    isConnected,
    connect,
    disconnect
  }
})
```

---

## База данных и миграции

### Работа с Alembic

```bash
# Создать новую миграцию (автоматическая генерация)
alembic revision --autogenerate -m "Description of changes"

# Создать пустую миграцию (ручная)
alembic revision -m "Description of changes"

# Применить все миграции
alembic upgrade head

# Откатить одну миграцию
alembic downgrade -1

# Показать текущую версию
alembic current

# Показать историю миграций
alembic history

# Показать SQL без выполнения
alembic upgrade head --sql
```

### Пример миграции

```python
"""Add user_level column

Revision ID: abc123def456
Revises: prev_revision_id
Create Date: 2024-01-15 10:30:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'abc123def456'
down_revision = 'prev_revision_id'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('users',
        sa.Column('level', sa.Integer(), nullable=False, server_default='1')
    )
    op.create_index(op.f('ix_users_level'), 'users', ['level'])

def downgrade() -> None:
    op.drop_index(op.f('ix_users_level'), table_name='users')
    op.drop_column('users', 'level')
```

---

## Тестирование

### Backend тесты

```bash
# Установить pytest и зависимости
pip install pytest pytest-asyncio pytest-cov httpx

# Запустить тесты
pytest

# С покрытием кода
pytest --cov=app --cov-report=html

# Запустить конкретный тест
pytest tests/test_raffles.py::test_create_raffle
```

### Пример теста

```python
# tests/test_raffles.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_get_active_raffles():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/raffles/active")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
```

### Frontend тесты

```bash
# Установить Vitest
npm install -D vitest @vue/test-utils

# Запустить тесты
npm run test

# С UI
npm run test:ui

# С покрытием
npm run test:coverage
```

---

## Стандарты кода

### Python (Backend)

- **PEP 8**: Следуйте стандартам Python
- **Type hints**: Используйте type hints везде
- **Docstrings**: Google style docstrings
- **Line length**: Максимум 100 символов
- **Import sorting**: `isort` для сортировки импортов

```python
from typing import List, Optional

async def get_raffles(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> List[Raffle]:
    """
    Get list of raffles from database.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of Raffle objects
    """
    query = select(Raffle).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
```

### TypeScript (Frontend)

- **ESLint**: Следуйте правилам ESLint
- **Prettier**: Автоматическое форматирование
- **Naming conventions**:
  - Components: PascalCase
  - Functions/variables: camelCase
  - Constants: UPPER_CASE
  - Types/Interfaces: PascalCase

```typescript
// Good
interface UserData {
  id: number
  name: string
}

const fetchUserData = async (userId: number): Promise<UserData> => {
  const response = await api.get(`/users/${userId}`)
  return response.data
}

const MAX_RETRIES = 3
```

### Git Commit Messages

Используйте [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add user profile page
fix: resolve wallet connection issue
docs: update API documentation
style: format code with prettier
refactor: reorganize store structure
test: add tests for raffle service
chore: update dependencies
```

---

## Git workflow

### Branch naming

- `main` - production ready code
- `develop` - development branch
- `feature/feature-name` - новые функции
- `fix/bug-description` - исправления
- `hotfix/critical-fix` - критические исправления

### Development workflow

```bash
# Создать feature branch
git checkout -b feature/new-feature develop

# Сделать изменения и commit
git add .
git commit -m "feat: implement new feature"

# Регулярно синхронизировать с develop
git fetch origin
git rebase origin/develop

# Push feature branch
git push origin feature/new-feature

# Создать Pull Request через GitHub
```

### Code Review checklist

- [ ] Код следует стандартам проекта
- [ ] Все тесты проходят
- [ ] Нет console.log / print statements
- [ ] Документация обновлена
- [ ] Нет конфликтов с develop
- [ ] Изменения протестированы локально
- [ ] Миграции базы данных работают корректно

---

## Полезные команды

### Backend

```bash
# Форматирование кода
black app/
isort app/

# Линтинг
flake8 app/
pylint app/

# Type checking
mypy app/

# Запуск REPL с контекстом приложения
python -m app.scripts.shell
```

### Frontend

```bash
# Форматирование
npm run format

# Линтинг
npm run lint

# Type checking
npm run type-check

# Build для production
npm run build

# Preview production build
npm run preview
```

---

## Дополнительные ресурсы

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vue.js 3 Documentation](https://vuejs.org/)
- [Pinia Documentation](https://pinia.vuejs.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [aiogram Documentation](https://docs.aiogram.dev/)
- [TON Documentation](https://ton.org/docs/)
- [TailwindCSS Documentation](https://tailwindcss.com/docs)
