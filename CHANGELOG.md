# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive setup documentation (SETUP.md) with detailed installation instructions for both Docker and non-Docker setups
- Development guide (DEVELOPMENT.md) with architecture overview, coding standards, and workflows
- Additional Makefile commands: `status`, `health`, `restore`
- Backup directory creation in Makefile backup command
- Enhanced help text in Makefile with detailed command descriptions
- Troubleshooting section in README.md
- Environment file (.env) created from .env.example with development defaults

### Changed
- **BREAKING**: Updated `docker-compose` commands to `docker compose` (v2 syntax) in Makefile
- Updated vue-tsc from ^1.8.27 to ^2.1.10 to fix build compatibility issues
- Updated TypeScript from ^5.3.0 to ^5.6.3
- Updated Vite from ^5.0.0 to ^5.4.11
- Improved README.md with better structure, badges, and links to documentation
- Enhanced Makefile backup command to use `-T` flag and save to `backups/` directory
- Updated Makefile restore command to accept FILE parameter for flexible restoration

### Fixed
- **vue-tsc build error**: Fixed "Search string not found: /supportedTSExtensions = .*(?=;)/" error by upgrading to vue-tsc 2.x
- **Docker Compose warning**: Removed obsolete `version: '3.8'` from docker-compose.yml
- **Dockerfile casing warning**: Changed `as builder` to `AS builder` in frontend/Dockerfile
- **Redis healthcheck**: Fixed healthcheck command to properly authenticate with Redis password
- **Makefile compatibility**: Updated all commands to use Docker Compose v2 syntax

### Improved
- Docker healthcheck for Redis now uses `--no-auth-warning` flag
- Backup and restore commands now work correctly with PostgreSQL in Docker
- Better error handling in Makefile commands
- More detailed environment variable documentation

## [1.0.0] - 2024-01-15

### Added
- Initial release of Web3 Raffle Bot
- FastAPI backend with async support
- Vue.js 3 frontend with TypeScript
- TON blockchain integration
- Telegram Bot integration with aiogram
- PostgreSQL database with SQLAlchemy ORM
- Redis caching layer
- Docker and Docker Compose configuration
- Three raffle types: Express, Standard, Premium
- Random.org integration for provably fair draws
- WebSocket support for real-time updates
- Automatic raffle creation and prize distribution
- Database migrations with Alembic
- Comprehensive API documentation with Swagger

### Security
- Telegram WebApp authentication
- Blockchain transaction validation
- Rate limiting
- CORS protection
- Environment-based configuration

---

## Version Comparison

### v1.0.0 → Unreleased

**Key Improvements:**
1. **Build System**: Fixed critical vue-tsc compatibility issue preventing Docker builds
2. **Docker Configuration**: Updated to modern Docker Compose v2 syntax
3. **Documentation**: Added 200+ pages of comprehensive documentation
4. **Developer Experience**: Improved Makefile with more commands and better descriptions
5. **Reliability**: Fixed Redis healthcheck and improved backup/restore procedures

**Breaking Changes:**
- Makefile now requires Docker Compose v2 (use `docker compose` instead of `docker-compose`)
- Frontend build requires newer versions of TypeScript (5.6.3+) and vue-tsc (2.1.10+)

**Migration Guide:**
```bash
# Update Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Clean old builds
make clean

# Rebuild with new versions
make build
make up
```

---

## Notes

### Versioning Strategy
- **Major version** (X.0.0): Breaking changes or major feature additions
- **Minor version** (0.X.0): New features, non-breaking changes
- **Patch version** (0.0.X): Bug fixes, documentation updates

### Deprecation Policy
- Deprecated features will be marked in the changelog
- Deprecated features will be supported for at least one minor version
- Breaking changes will only occur in major version updates

### Security Updates
Security vulnerabilities will be patched immediately and released as patch versions, regardless of the regular release schedule.

---

## Links

- [Repository](https://github.com/f2re/raffle-web3-bot)
- [Issues](https://github.com/f2re/raffle-web3-bot/issues)
- [Pull Requests](https://github.com/f2re/raffle-web3-bot/pulls)
