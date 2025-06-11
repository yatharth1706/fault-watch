# Fault Watch

A FastAPI-based error monitoring and tracking system.

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd fault-watch
   ```

2. **Set up environment variables**
   ```bash
   cp .env-copy .env
   # Edit .env with your database credentials
   ```

3. **Start the application**
   ```bash
   pnpm dev
   ```

That's it! The application will:
- Start PostgreSQL and Redis services
- Automatically run database migrations
- Start the FastAPI server on port 8001

## What happens automatically:

✅ **Database Setup**: PostgreSQL starts with your configured credentials  
✅ **Migrations**: All database migrations are applied automatically  
✅ **API Server**: FastAPI server starts with auto-discovered routers  
✅ **Health Check**: Visit `http://localhost:8001/health` to verify everything is working  

## Manual Setup (without Docker)

If you prefer to run without Docker:

1. Install dependencies:
   ```bash
   cd backend
   uv sync
   ```

2. Set up your database and run migrations:
   ```bash
   alembic upgrade head
   ```

3. Start the server:
   ```bash
   uvicorn api.main:app --reload --port 8001
   ```

## Project Structure

```
backend/
├── api/
│   ├── main.py          # Auto-discovers and includes all routers
│   ├── errors/          # Error tracking endpoints
│   └── [other-modules]/ # Future API modules
├── db/
│   ├── migrations/      # Alembic migrations
│   └── models/          # SQLAlchemy models
└── start.sh            # Startup script with migrations
```

## Adding New API Modules

1. Create a new directory in `backend/api/` (e.g., `users/`)
2. Add a `controller.py` file with a `router` object
3. The router will be automatically discovered and included!

Example:
```python
# backend/api/users/controller.py
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
async def get_users():
    return {"users": []}
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ and pnpm 8+

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd fault-watch
   ```

2. **Install pnpm (if not already installed)**
   ```bash
   npm install -g pnpm
   ```

3. **Set up environment variables**
   ```bash
   cp .env-copy .env
   # Edit .env with your configuration
   ```

4. **Start the development environment**
   ```bash
   pnpm dev
   ```

## 📋 Available Scripts

### Development
- `pnpm dev` - Start all services (backend, database, redis)
- `pnpm dev:backend` - Start only the backend service
- `pnpm dev:db` - Start only database and redis services

### Database Management
- `pnpm db:migrate` - Run all pending migrations
- `pnpm db:migrate:down` - Downgrade one migration
- `pnpm db:migrate:base` - Downgrade to base (remove all migrations)
- `pnpm db:revision "message"` - Create auto-generated migration


## 🗄️ Database Commands

### Creating Migrations
```bash
# Auto-generate migration from model changes
pnpm db:revision "add user table"

# Create manual migration
pnpm db:revision:manual "custom migration"
```

### Running Migrations
```bash
# Apply all pending migrations
pnpm db:migrate

# Downgrade one step
pnpm db:migrate:down

# Downgrade to base (remove all migrations)
pnpm db:migrate:base
```

## 🌐 API Endpoints

- **Health Check**: `GET /health`
- **Error Endpoints**: 
  - `GET /errors/` - Get all errors
  - `POST /errors/` - Ingest new error