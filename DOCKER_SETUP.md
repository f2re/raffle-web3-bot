# Docker Setup - Shared Container Configuration

## Overview

This project now uses **existing PostgreSQL and Redis containers** from the `postgres_timecapsule_network` instead of creating new ones. This approach:

- **Prevents port conflicts** (no more "port already allocated" errors)
- **Shares resources** efficiently across multiple projects
- **Uses internal networking** (no exposed ports to host)

## Architecture

```
postgres_timecapsule_network (172.18.0.0/16)
├── timecapsule_postgres (172.18.0.2) - Shared PostgreSQL
├── timecapsule_bot (172.18.0.4)
├── bg_removal_bot (172.18.0.3)
│   └── bg-remove-bot-redis-1 - Shared Redis
└── raffle_backend (new) - Your bot
    └── raffle_frontend (new) - Your web interface
```

## Changes Made

### 1. Docker Compose Configuration

**Removed:**
- Standalone `postgres` service
- Standalone `redis` service
- Port bindings (`ports:` replaced with `expose:`)
- Dedicated `raffle_network`

**Updated:**
- All services now connect to `postgres_timecapsule_network` (external)
- Backend connects to `timecapsule_postgres:5432`
- Backend connects to `bg-remove-bot-redis-1:6379`
- Only internal ports exposed (no host bindings)

### 2. Environment Variables

**Updated in `.env.example`:**
```bash
# Old
DATABASE_URL=postgresql://postgres:password@postgres:5432/raffle_web3

# New
DATABASE_URL=postgresql://postgres:password@timecapsule_postgres:5432/raffle_web3
REDIS_URL=redis://:password@bg-remove-bot-redis-1:6379/0
```

### 3. Makefile Commands

**New command:**
```bash
make create-db  # Creates raffle_web3 database in existing PostgreSQL
```

**Updated commands:**
- `make up` - Now shows network info instead of port URLs
- `make backup` - Uses `timecapsule_postgres` container
- `make restore` - Uses `timecapsule_postgres` container

## Setup Instructions

### Step 1: Ensure Existing Containers are Running

```bash
# Check if required containers are running
docker ps | grep -E "timecapsule_postgres|bg-remove-bot-redis-1"
```

You should see:
```
timecapsule_postgres  - PostgreSQL 16
bg-remove-bot-redis-1 - Redis 7
```

### Step 2: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your actual credentials
nano .env
```

**Important:** Use the **same PostgreSQL and Redis passwords** as the existing containers.

### Step 3: Create Database

```bash
# Create the raffle_web3 database in existing PostgreSQL
make create-db
```

This runs:
```bash
docker exec -it timecapsule_postgres psql -U postgres -c "CREATE DATABASE raffle_web3;"
```

### Step 4: Build and Start

```bash
# Build images
make build

# Start services
make up
```

### Step 5: Initialize Database

```bash
# Run migrations and seed data
make init
```

## Verification

### Check Container Network

```bash
# Inspect the network
docker network inspect postgres_timecapsule_network

# You should see all containers including raffle_backend and raffle_frontend
```

### Check Container Status

```bash
make status
# or
docker compose ps
```

### Check Logs

```bash
# All services
make logs

# Specific service
docker compose logs -f backend
```

### Test Database Connection

```bash
# Connect to PostgreSQL
docker exec -it timecapsule_postgres psql -U postgres -d raffle_web3

# List databases
\l

# List tables in raffle_web3
\dt

# Exit
\q
```

### Test Redis Connection

```bash
# Connect to Redis
docker exec -it bg-remove-bot-redis-1 redis-cli -a your_redis_password

# Test connection
PING  # Should return PONG

# Check keys
KEYS *

# Exit
exit
```

## Troubleshooting

### Error: "network postgres_timecapsule_network not found"

**Solution:** The network doesn't exist. Create it:
```bash
docker network create postgres_timecapsule_network
```

Then attach existing containers:
```bash
docker network connect postgres_timecapsule_network timecapsule_postgres
docker network connect postgres_timecapsule_network bg-remove-bot-redis-1
```

### Error: "database raffle_web3 does not exist"

**Solution:** Run the database creation command:
```bash
make create-db
```

Or manually:
```bash
docker exec -it timecapsule_postgres psql -U postgres -c "CREATE DATABASE raffle_web3;"
```

### Error: "connection refused to timecapsule_postgres"

**Possible causes:**
1. PostgreSQL container not running
2. Wrong password in `.env`
3. Container not on the same network

**Solution:**
```bash
# Check if postgres is running
docker ps | grep timecapsule_postgres

# Check network membership
docker inspect timecapsule_postgres | grep NetworkMode

# Verify credentials
docker exec -it timecapsule_postgres psql -U postgres -c "\l"
```

### Error: "connection refused to bg-remove-bot-redis-1"

**Possible causes:**
1. Redis container not running
2. Wrong password in `.env`

**Solution:**
```bash
# Check if redis is running
docker ps | grep bg-remove-bot-redis-1

# Test redis connection with password
docker exec -it bg-remove-bot-redis-1 redis-cli -a your_password PING
```

## Port Information

Since we're using internal networking, services are **not accessible from the host**. To access them:

### Option 1: Through Another Container

```bash
# Access backend API from within the network
docker run --rm --network postgres_timecapsule_network curlimages/curl:latest \
  curl http://raffle_backend:8000/api/v1/health
```

### Option 2: Add Port Binding for Development

If you need to access services from your host machine for development, temporarily add:

```yaml
# In docker-compose.yml
services:
  backend:
    ports:
      - "127.0.0.1:8000:8000"  # Bind only to localhost
```

**Important:** Don't commit port bindings that conflict with existing services!

## Benefits of This Setup

1. **Resource Efficiency:** One PostgreSQL and Redis instance for multiple projects
2. **No Port Conflicts:** All communication happens internally
3. **Security:** Services not exposed to host network
4. **Scalability:** Easy to add more services to the shared network
5. **Consistency:** All bots use the same database and cache infrastructure

## Backup and Restore

### Backup

```bash
# Create backup of raffle_web3 database
make backup
```

Backups are stored in `backups/backup_YYYYMMDD_HHMMSS.sql`

### Restore

```bash
# Restore from specific backup file
make restore FILE=backups/backup_20250101_120000.sql
```

## Additional Commands

```bash
# Show all available commands
make help

# View service status
make status

# Check health of services
make health

# Restart services
make restart

# Stop services
make down

# Clean up (warning: removes volumes!)
make clean
```

## Migration from Old Setup

If you're migrating from the old setup with standalone containers:

1. **Export data from old containers:**
   ```bash
   docker exec raffle_postgres pg_dump -U postgres raffle_web3 > migration_backup.sql
   ```

2. **Stop and remove old containers:**
   ```bash
   docker compose down -v
   ```

3. **Create new database:**
   ```bash
   make create-db
   ```

4. **Import data:**
   ```bash
   docker exec -i timecapsule_postgres psql -U postgres -d raffle_web3 < migration_backup.sql
   ```

5. **Start new services:**
   ```bash
   make build
   make up
   ```

## Security Considerations

1. **Use strong passwords** for PostgreSQL and Redis
2. **Don't expose ports** unless necessary
3. **Keep credentials in .env** (not in docker-compose.yml)
4. **Add .env to .gitignore**
5. **Regularly backup** your database

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Docker logs: `make logs`
3. Verify network configuration: `docker network inspect postgres_timecapsule_network`
4. Check container status: `docker ps`
