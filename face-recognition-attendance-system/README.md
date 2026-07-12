# Face Recognition Attendance System

A production-grade AI-powered attendance system using face recognition technology, built for scale (100,000+ users).

## Architecture Overview

```
face-recognition-attendance-system/
├── frontend/          # React 19 + TypeScript + Vite SPA
├── backend/           # FastAPI + Python 3.12 monolith (modular)
├── docs/              # Project documentation
├── datasets/          # Face datasets (gitignored)
├── models/            # Trained ML models (gitignored)
├── docker/            # Dockerfiles for each service
├── scripts/           # Dev/CI automation scripts
├── .github/           # GitHub Actions workflows
├── docker-compose.yml # Local development orchestration
└── README.md          # This file
```

## Directory Breakdown

### `frontend/`
React 19 SPA consuming the FastAPI backend. Uses Vite for build, Tailwind CSS for styling, React Router for client-side routing, React Query for server state, Zustand for client state, and Axios for HTTP.

| Path               | Purpose                                    |
|--------------------|--------------------------------------------|
| `src/assets/`      | Static images, icons, fonts                |
| `src/components/`  | Reusable UI components (common, forms, layout, ui) |
| `src/pages/`       | Page-level components by feature domain    |
| `src/routes/`      | Route definitions and guards               |
| `src/hooks/`       | Custom React hooks                         |
| `src/services/`    | API client layer (Axios instance + modules)|
| `src/store/`       | Zustand stores for client state            |
| `src/types/`       | TypeScript type definitions                |
| `src/utils/`       | Utility/helper functions                   |
| `src/constants/`   | App-wide constants                         |
| `src/styles/`      | Global CSS / Tailwind layers               |

### `backend/`
FastAPI application following a modular, service-oriented structure.

| Path                  | Purpose                                      |
|-----------------------|----------------------------------------------|
| `app/api/`            | Route handlers and dependency injection      |
| `app/core/`           | Config, security, logging                    |
| `app/database/`       | DB connection, session management            |
| `app/models/`         | SQLAlchemy ORM models                        |
| `app/schemas/`        | Pydantic request/response schemas            |
| `app/services/`       | Business logic layer                         |
| `app/repositories/`   | Data access layer (repository pattern)       |
| `app/middleware/`     | ASGI middleware (CORS, rate-limit, etc.)     |
| `app/utils/`          | Shared utilities                             |
| `app/face_recognition/` | Face detection, encoding, recognition engine |
| `app/attendance/`     | Attendance domain module                     |
| `app/students/`       | Student management domain module             |
| `app/auth/`           | Authentication & authorization module        |
| `app/reports/`        | Reporting & analytics module                 |
| `app/tests/`          | Test suite (unit, integration, e2e)          |
| `alembic/`            | Database migration scripts                   |
| `requirements/`       | Pinned dependency files per environment      |

### `docs/`
Living documentation for the project.

| Path               | Purpose                  |
|--------------------|--------------------------|
| `architecture/`    | C4 diagrams, ADRs        |
| `api/`             | OpenAPI specs, endpoints |
| `database/`        | ERD, migration guide     |
| `setup/`           | Onboarding guide         |

### `docker/`
Dockerfiles for each service. The root `docker-compose.yml` orchestrates them for local development.

### `scripts/`
Automation scripts for development workflow.

| Script        | Purpose                    |
|---------------|----------------------------|
| `setup.sh`    | First-time project setup   |
| `run.sh`      | Start all services         |
| `format.sh`   | Auto-format code           |
| `lint.sh`     | Run linters                |
| `test.sh`     | Run test suites            |

### `datasets/`
Contains face image datasets used for training and evaluation. Contents are gitignored.

### `models/`
Stores trained InsightFace models and ONNX runtime artifacts. Contents are gitignored.

## Getting Started

See `docs/setup/` for setup instructions.

## Tech Stack

- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, React Router, Axios, React Query, Zustand
- **Backend**: Python 3.12, FastAPI, SQLAlchemy, Alembic, Pydantic, InsightFace, OpenCV, ONNX Runtime
- **Database**: PostgreSQL
- **Deployment**: Docker, Docker Compose, Nginx
- **Code Quality**: ESLint, Prettier, Black, isort, Ruff, mypy
