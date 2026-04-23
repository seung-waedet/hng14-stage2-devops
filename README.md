# HNG Stage 2 DevOps - Job Processing System

A containerized job processing system with Frontend, API, Worker, and Redis.

## Architecture

```
┌────────────┐     ┌─────────────┐     ┌────────────┐
│  Frontend  │────>│  API        │────>│  Worker    │
│  (Node.js) │     │  (FastAPI)  │     │  (Python)  │
└────────────┘     └─────────────┘     └────────────┘
                          │
                          v
                    ┌────────────┐
                    │   Redis    │
                    └────────────┘
```

## Prerequisites

- Docker >= 20.10
- Docker Compose >= 2.0
- Git

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/seung-waedet/hng14-stage2-devops
cd hng14-stage2-devops
```

### 2. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` if needed (defaults work for local development):

### 3. Build and Start

```bash
docker-compose up --build
```

### 4. Verify Services

Check health of all services:

```bash
# API Health
curl http://localhost:8000/health

# Response: {"status": "healthy"}
```

### 5. Access Frontend

Open http://localhost:3000 in your browser.

Click "Submit New Job" to create a job. The worker will pick it up and mark it as completed after 2 seconds.

## Services

| Service | Port | Description |
|---------|------|-------------|
| frontend | 3000 | Web UI for job submission |
| api | 8000 | REST API for job management |
| redis | 6379 | Job queue and status storage (internal) |

## Development

### Running Locally (without Docker)

**API:**
```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload
```

**Worker:**
```bash
cd worker
pip install -r requirements.txt
python worker.py
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

**Note:** For local development, ensure Redis is running on localhost:6379.

### Running Tests

```bash
# API tests
cd api
pip install -r requirements.txt
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=. --cov-report=html
```

## CI/CD Pipeline

The pipeline runs automatically on push/PR with stages:

1. **Lint** - flake8, eslint, hadolint
2. **Test** - pytest with coverage
3. **Build** - Docker images with SHA tags
4. **Security Scan** - Trivy vulnerability scan
5. **Integration Test** - Full stack test
6. **Deploy** - Rolling update (main branch only)

See `.github/workflows/ci-cd.yml` for details.

## Project Structure

```
.
├── api/
│   ├── Dockerfile
│   ├── main.py          # FastAPI application
│   ├── requirements.txt
│   └── tests/
│       └── test_api.py  # Unit tests
├── frontend/
│   ├── Dockerfile
│   ├── app.js           # Express application
│   ├── package.json
│   └── views/
│       └── index.html   # Web UI
├── worker/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── worker.py        # Job processor
├── docker-compose.yml
├── .env.example
├── .gitignore
├── FIXES.md
└── README.md
```

## Troubleshooting

### Services won't start

Check logs:
```bash
docker-compose logs api
docker-compose logs worker
docker-compose logs frontend
```

### Redis connection issues

Verify Redis is healthy:
```bash
docker-compose exec redis redis-cli ping
```

Should return: `PONG`

### API returns 500 errors

Check that all services are on the same network:
```bash
docker network inspect hng14-stage2-devops_app-network
```

## Stopping the Stack

```bash
docker-compose down
```

To remove volumes (clears all job data):
```bash
docker-compose down -v
```