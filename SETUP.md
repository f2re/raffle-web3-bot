# Полное руководство по установке и запуску Web3 Raffle Bot

## Оглавление

1. [Требования](#требования)
2. [Установка Docker](#установка-docker)
3. [Запуск с Docker](#запуск-с-docker)
4. [Запуск без Docker](#запуск-без-docker)
5. [Управление проектом](#управление-проектом)
6. [Резервное копирование](#резервное-копирование)
7. [Устранение неполадок](#устранение-неполадок)

---

## Требования

### Для запуска с Docker:
- Docker 20.10+
- Docker Compose v2 (команда `docker compose`)
- Git
- Минимум 2GB RAM
- Минимум 10GB свободного места на диске

### Для запуска без Docker:
- Python 3.11+
- Node.js 20+
- PostgreSQL 14+
- Redis 7+
- Git

---

## Установка Docker

### Ubuntu/Debian

```bash
# Обновить индекс пакетов
sudo apt-get update

# Установить зависимости
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Добавить официальный GPG ключ Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Настроить репозиторий
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Установить Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Добавить текущего пользователя в группу docker
sudo usermod -aG docker $USER

# Перезайти в систему или выполнить:
newgrp docker

# Проверить установку
docker --version
docker compose version
```

### CentOS/RHEL

```bash
# Удалить старые версии
sudo yum remove docker docker-client docker-client-latest docker-common docker-latest

# Установить зависимости
sudo yum install -y yum-utils

# Добавить репозиторий Docker
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Установить Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Запустить Docker
sudo systemctl start docker
sudo systemctl enable docker

# Добавить пользователя в группу docker
sudo usermod -aG docker $USER
newgrp docker

# Проверить установку
docker --version
docker compose version
```

---

## Запуск с Docker

### 1. Клонировать репозиторий

```bash
git clone https://github.com/f2re/raffle-web3-bot.git
cd raffle-web3-bot
```

### 2. Создать и настроить .env файл

```bash
# Скопировать пример конфигурации
cp .env.example .env

# Отредактировать .env файл
nano .env  # или используйте любой другой текстовый редактор
```

### 3. Обязательные параметры для заполнения в .env

```env
# === PostgreSQL ===
POSTGRES_PASSWORD=your_strong_password_here  # Используйте надежный пароль

# === Redis ===
REDIS_PASSWORD=your_redis_password_here  # Используйте надежный пароль

# === Backend ===
SECRET_KEY=your_secret_key_at_least_32_characters_long  # Минимум 32 символа

# === Telegram Bot ===
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz  # Получить у @BotFather
ADMIN_USER_ID=123456789  # Ваш Telegram user ID

# === TON Blockchain ===
RAFFLE_WALLET_ADDRESS=UQxxxx...  # Адрес TON кошелька
RAFFLE_WALLET_MNEMONIC=word1 word2 ... word24  # 24-словная мнемоническая фраза
TON_CENTER_API_KEY=your_toncenter_api_key  # Получить на toncenter.com

# === Random.org ===
RANDOM_ORG_API_KEY=your_random_org_api_key  # Получить на random.org

# === Frontend ===
VITE_API_URL=https://your-backend.com/api/v1  # URL вашего backend API
VITE_WS_URL=wss://your-backend.com/ws  # WebSocket URL
VITE_RAFFLE_WALLET=UQxxxx...  # Тот же адрес TON кошелька
VITE_TON_MANIFEST_URL=https://your-domain.com/tonconnect-manifest.json
```

### 4. Получить необходимые API ключи

#### Telegram Bot Token:
1. Открыть Telegram и найти @BotFather
2. Отправить `/newbot`
3. Следовать инструкциям для создания бота
4. Скопировать токен бота

#### TON Center API Key:
1. Перейти на https://toncenter.com
2. Зарегистрироваться или войти
3. Создать новый API ключ в разделе API Keys

#### Random.org API Key:
1. Перейти на https://api.random.org/api-keys
2. Зарегистрироваться для получения бесплатного API ключа
3. Скопировать ключ из личного кабинета

#### Telegram User ID:
1. Открыть Telegram и найти @userinfobot
2. Отправить `/start`
3. Скопировать ваш User ID

### 5. Собрать и запустить проект

```bash
# Собрать Docker образы
make build

# Запустить все сервисы
make up

# Проверить статус сервисов
make status

# Просмотреть логи
make logs
```

### 6. Инициализировать базу данных

```bash
# Выполнить миграции и создать начальные розыгрыши
make init
```

### 7. Проверить работу сервисов

```bash
# Проверить здоровье сервисов
make health

# Backend API доступен на: http://localhost:8000
# Frontend доступен на: http://localhost:3000
# API документация: http://localhost:8000/docs
```

---

## Запуск без Docker

### 1. Установить PostgreSQL

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Создать базу данных и пользователя
sudo -u postgres psql << EOF
CREATE DATABASE raffle_web3;
CREATE USER raffle_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE raffle_web3 TO raffle_user;
\q
EOF
```

#### macOS:
```bash
brew install postgresql@14
brew services start postgresql@14

# Создать базу данных
createdb raffle_web3
```

### 2. Установить Redis

#### Ubuntu/Debian:
```bash
sudo apt-get install -y redis-server
sudo systemctl start redis
sudo systemctl enable redis

# Настроить пароль
sudo nano /etc/redis/redis.conf
# Найти и раскомментировать: requirepass your_redis_password
sudo systemctl restart redis
```

#### macOS:
```bash
brew install redis
brew services start redis

# Настроить пароль
echo "requirepass your_redis_password" >> /usr/local/etc/redis.conf
brew services restart redis
```

### 3. Установить Python и зависимости

```bash
# Установить Python 3.11
sudo apt-get install -y python3.11 python3.11-venv python3-pip

# Перейти в директорию backend
cd backend

# Создать виртуальное окружение
python3.11 -m venv venv

# Активировать виртуальное окружение
source venv/bin/activate  # Linux/macOS
# или
.\venv\Scripts\activate  # Windows

# Установить зависимости
pip install -r requirements.txt
```

### 4. Установить Node.js и зависимости

```bash
# Установить Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Перейти в директорию frontend
cd ../frontend

# Установить зависимости
npm install
```

### 5. Настроить .env файлы

#### Backend (.env в корне проекта):
```env
# Database
DATABASE_URL=postgresql://raffle_user:your_password@localhost:5432/raffle_web3
REDIS_URL=redis://:your_redis_password@localhost:6379/0

# App settings
ENVIRONMENT=development
LOG_LEVEL=INFO
SECRET_KEY=your_secret_key_at_least_32_characters_long

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
ADMIN_USER_ID=your_user_id

# TON Blockchain
RAFFLE_WALLET_ADDRESS=your_wallet_address
RAFFLE_WALLET_MNEMONIC=your mnemonic phrase
TON_CENTER_API_KEY=your_api_key

# Random.org
RANDOM_ORG_API_KEY=your_api_key

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

#### Frontend (.env.local в директории frontend):
```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
VITE_RAFFLE_WALLET=your_wallet_address
VITE_TON_MANIFEST_URL=http://localhost:5173/tonconnect-manifest.json
```

### 6. Запустить миграции базы данных

```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

### 7. Запустить сервисы

#### Terminal 1 - Backend:
```bash
cd backend
source venv/bin/activate
python -m app.main
```

#### Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

### 8. Проверить работу

- Backend API: http://localhost:8000
- Frontend: http://localhost:5173
- API документация: http://localhost:8000/docs

---

## Управление проектом

### Команды Makefile (для Docker)

```bash
# Показать все доступные команды
make help

# Собрать образы с чистым кэшем
make build

# Запустить сервисы
make up

# Остановить сервисы
make down

# Перезапустить сервисы
make restart

# Показать логи
make logs

# Показать статус сервисов
make status

# Проверить здоровье сервисов
make health

# Инициализировать базу данных
make init

# Создать резервную копию
make backup

# Восстановить из резервной копии
make restore FILE=backups/backup_YYYYMMDD_HHMMSS.sql

# Очистить все данные и volumes
make clean
```

### Управление отдельными сервисами

```bash
# Перезапустить только backend
docker compose restart backend

# Просмотреть логи только backend
docker compose logs -f backend

# Просмотреть логи только frontend
docker compose logs -f frontend

# Выполнить команду в контейнере backend
docker compose exec backend python -m app.scripts.some_script

# Подключиться к PostgreSQL
docker compose exec postgres psql -U postgres raffle_web3

# Подключиться к Redis CLI
docker compose exec redis redis-cli -a your_redis_password
```

---

## Резервное копирование

### Автоматическое резервное копирование (с Docker)

```bash
# Создать резервную копию базы данных
make backup

# Резервная копия будет сохранена в директории backups/ с меткой времени
# Например: backups/backup_20240115_143022.sql
```

### Восстановление из резервной копии

```bash
# Восстановить базу данных из файла
make restore FILE=backups/backup_20240115_143022.sql
```

### Ручное резервное копирование (без Docker)

```bash
# Создать резервную копию PostgreSQL
pg_dump -U raffle_user raffle_web3 > backup_$(date +%Y%m%d_%H%M%S).sql

# Восстановить из резервной копии
psql -U raffle_user raffle_web3 < backup_20240115_143022.sql
```

### Резервное копирование Redis

```bash
# С Docker
docker compose exec redis redis-cli -a your_redis_password SAVE
docker compose cp redis:/data/dump.rdb ./backups/redis_dump_$(date +%Y%m%d_%H%M%S).rdb

# Без Docker
redis-cli -a your_redis_password SAVE
cp /var/lib/redis/dump.rdb ./backups/redis_dump_$(date +%Y%m%d_%H%M%S).rdb
```

### Настройка автоматического резервного копирования

Создайте cron задачу для автоматического резервного копирования:

```bash
# Открыть crontab
crontab -e

# Добавить задачу для ежедневного резервного копирования в 2:00 AM
0 2 * * * cd /path/to/raffle-web3-bot && make backup

# Добавить задачу для очистки старых резервных копий (старше 30 дней)
0 3 * * * find /path/to/raffle-web3-bot/backups -name "backup_*.sql" -mtime +30 -delete
```

---

## Устранение неполадок

### Проблема: vue-tsc build error

**Ошибка:**
```
Search string not found: "/supportedTSExtensions = .*(?=;)/"
```

**Решение:**
Эта проблема возникает из-за несовместимости версий. Убедитесь, что в `frontend/package.json`:
```json
"vue-tsc": "^2.1.10",
"typescript": "^5.6.3"
```

### Проблема: Docker compose version warning

**Ошибка:**
```
WARN[0000] the attribute `version` is obsolete
```

**Решение:**
Удалена строка `version: '3.8'` из `docker-compose.yml` (уже исправлено).

### Проблема: Redis healthcheck fails

**Ошибка:**
```
redis healthcheck failed
```

**Решение:**
Проверьте правильность пароля Redis в `.env` файле. Healthcheck теперь использует правильную команду с аутентификацией.

### Проблема: Backend не может подключиться к PostgreSQL

**Решение:**
1. Проверьте, что PostgreSQL запущен:
   ```bash
   docker compose ps postgres  # с Docker
   sudo systemctl status postgresql  # без Docker
   ```

2. Проверьте правильность DATABASE_URL в .env

3. Убедитесь, что пароли в .env совпадают

### Проблема: Frontend не может подключиться к Backend

**Решение:**
1. Проверьте, что Backend запущен и доступен:
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

2. Проверьте CORS настройки в Backend .env:
   ```env
   CORS_ORIGINS=http://localhost:5173,http://localhost:3000
   ```

3. Проверьте VITE_API_URL в Frontend .env

### Проблема: Порты уже заняты

**Ошибка:**
```
Bind for 0.0.0.0:8000 failed: port is already allocated
```

**Решение:**
1. Найти процесс, использующий порт:
   ```bash
   sudo lsof -i :8000
   ```

2. Остановить процесс или изменить порт в .env:
   ```env
   BACKEND_PORT=8001
   FRONTEND_PORT=3001
   ```

### Проблема: Out of memory

**Решение:**
1. Увеличьте память Docker в настройках Docker Desktop

2. Или ограничьте память для сервисов в docker-compose.yml:
   ```yaml
   services:
     backend:
       deploy:
         resources:
           limits:
             memory: 512M
   ```

### Проблема: Permission denied

**Решение:**
```bash
# Добавить пользователя в группу docker
sudo usermod -aG docker $USER
newgrp docker

# Изменить права на директории
sudo chown -R $USER:$USER .
```

### Логи и отладка

```bash
# Просмотр логов всех сервисов
make logs

# Просмотр логов конкретного сервиса
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres
docker compose logs -f redis

# Проверка состояния контейнеров
docker compose ps

# Проверка использования ресурсов
docker stats

# Подключение к контейнеру для отладки
docker compose exec backend sh
docker compose exec frontend sh
```

### Очистка и перезапуск

```bash
# Полная очистка и пересборка
make clean
make build
make up
make init

# Только перезапуск
make restart

# Остановка и запуск
make down
make up
```

---

## Дополнительные ресурсы

- [Документация Docker](https://docs.docker.com/)
- [Документация Docker Compose](https://docs.docker.com/compose/)
- [Документация FastAPI](https://fastapi.tiangolo.com/)
- [Документация Vue.js](https://vuejs.org/)
- [Документация TON](https://ton.org/docs/)
- [Документация Telegram Bots](https://core.telegram.org/bots)

---

## Поддержка

Если у вас возникли проблемы, не описанные в этом руководстве:

1. Проверьте логи: `make logs`
2. Проверьте статус сервисов: `make health`
3. Создайте issue на GitHub: https://github.com/f2re/raffle-web3-bot/issues
