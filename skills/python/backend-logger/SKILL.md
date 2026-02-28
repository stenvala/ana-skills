---
name: backend-logger
description: Backend logging patterns and infrastructure for Python API and worker processes. Use when adding logging to new services, routers, or worker processors, setting up log files/directories, configuring log rotation, fixing permission issues, or troubleshooting production logging. Covers the logging module (src/shared/logging.py), API middleware logging, worker-side logger usage, transaction IDs, systemd LOG_ROOT configuration, nginx/gunicorn logs, and file ownership/permissions.
---

# Backend Logger

@reference src/shared/logging.py
@reference src/api/middleware.py
@reference src/api/main.py
@reference src/worker/main.py

## Architecture Overview

All logging is centralized in `src/shared/logging.py`. Both API and worker use **file-only loggers** (no stdout) via `get_file_logger()`. The log directory is determined by the `LOG_ROOT` environment variable, falling back to `{repo_root}/logs`.

### Core Principle: Logger Injection

**ALL services must accept `logger: logging.Logger` as the first constructor argument.** The logger is never created inside a service — it is always injected from the caller:

- **API context**: Middleware initializes the logger and stores it on `request.state`. Dependency injectors in `src/api/dependencies/` extract it and pass it to services.
- **Worker context**: `worker/main.py` initializes the logger. Processors and services receive it as an argument.

This ensures consistent logger configuration across the entire call chain.

### Log Files

| File | Writer | Owner (remote) | Created by |
|------|--------|-----------------|------------|
| `api.log` / `api.log.1`..`.10` | API process (gunicorn workers) | `www-data:www-data` | `get_file_logger("api")` |
| `worker.log` / `worker.log.1`..`.10` | Worker process | `stenvala:stenvala` | `get_file_logger("worker")` |
| `access-gunicorn.log` | Gunicorn | `www-data:www-data` | Gunicorn `--access-logfile` flag |
| `error-gunicorn.log` | Gunicorn | `www-data:www-data` | Gunicorn `--error-logfile` flag |
| `access-nginx.log` | Nginx | `www-data:root` | Nginx `access_log` directive |
| `error-nginx.log` | Nginx | `www-data:root` | Nginx `error_log` directive |
| `start_services.log` | Local dev orchestrator | current user | `get_logger("start_services", add_file_handler=True)` |

### Local Development

Only `api.log`, `worker.log`, and `start_services.log` are relevant locally. They go to `{repo_root}/logs/`.

The `start_services.py` orchestrator sets `LOG_ROOT` before importing shared modules:
```python
if "LOG_ROOT" not in os.environ:
    os.environ["LOG_ROOT"] = str(repo_root / "logs")
```

### Remote Production

All 6 log files live in `{REMOTE_BASE}/logs/`. The `LOG_ROOT` env var is set in both systemd service files:
```ini
Environment="LOG_ROOT={{REMOTE_BASE}}/logs"
```

## Logger Factory Functions

| Function | Output | Use case |
|----------|--------|----------|
| `get_file_logger(name)` | File only (no stdout) | API and worker processes — prevents log noise in gunicorn/systemd stdout |
| `get_logger(name, add_file_handler=True)` | Stdout + optional file | `start_services.py` orchestrator — needs terminal output for local dev |

Both use `ReadableFormatter` and `RotatingFileHandler` (1 MB, 10 backups).

### `get_file_logger` (API & worker)

```python
from shared.logging import get_file_logger

logger = get_file_logger("api")  # writes to {LOG_ROOT}/api.log
logger = get_file_logger("worker", force_reconfigure=True)  # fresh file handles
```

- `force_reconfigure=True` clears existing handlers (needed after fork/reload)
- `propagate = False` prevents duplicate output
- Falls back to console on `OSError` with stderr warning

### `get_logger` (local dev orchestrator only)

```python
from shared.logging import get_logger

logger = get_logger("start_services", add_file_handler=True)
```

- Always has stdout handler
- Optional file handler when `add_file_handler=True`

## Transaction IDs

Transaction IDs correlate all log lines for a single request (API) or job (worker). `ReadableFormatter` automatically prepends `[transaction-id]` when set.

```python
from shared.logging import set_transaction_id, get_transaction_id

set_transaction_id("some-correlation-id")
# All log output now prefixed with [some-correlation-id]
logger.info("processing")  # => [some-correlation-id] 2025-... - name - INFO - processing

set_transaction_id("")  # clear when done
```

Uses `ContextVar` — safe for async/concurrent contexts.

## StructuredLogger

Wraps a standard `logging.Logger` to add extra keyword fields appended as `| key=value`:

```python
from shared.logging import StructuredLogger

structured = StructuredLogger(logger)
structured.info("REQUEST_START", method="GET", path="/api/health")
# => 2025-... - api - INFO - REQUEST_START | method=GET path=/api/health
```

Methods: `info()`, `error()`, `warning()`, `critical()`, `debug()` — all accept `**kwargs`.

## API Logging Pattern

### Middleware (`src/api/middleware.py`)

The API logger is initialized once at module level and wrapped in `StructuredLogger`. The middleware stores the raw logger on `request.state` so dependency injectors can pass it to services:

```python
from shared.logging import StructuredLogger, get_file_logger, set_transaction_id

api_logger = get_file_logger("api")

class ApiMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.logger = StructuredLogger(api_logger)

    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())
        set_transaction_id(request_id)

        # Make logger available to dependency injectors via request.state
        request.state.logger = api_logger

        self.logger.info("REQUEST_START", method=request.method, path=str(request.url.path))
        response = await call_next(request)
        self.logger.info("REQUEST_END", method=request.method, path=str(request.url.path), status_code=response.status_code)
        return response
```

The middleware handles ALL error logging — services and routers do NOT catch or log exceptions.

### Gunicorn multiprocessing (`src/api/main.py`)

Each gunicorn worker forks and needs fresh file handles:

```python
def reinit_logging_on_worker_start(worker):
    get_file_logger("api", force_reconfigure=True)
```

### Dependency Injection: Logger to Services (`src/api/dependencies/`)

**All service dependency injectors live in `src/api/dependencies/`, NOT in router files.** Routers never define `_get_service()` locally — they import dependency functions from `src/api/dependencies/`.

The logger is extracted from `request.state` (set by middleware) and injected into every service:

```python
# src/api/dependencies/database.py
from typing import Generator
from sqlmodel import Session
from shared.db.db_context import DBContext

def get_db_session() -> Generator[Session, None, None]:
    """Dependency for database session injection."""
    with DBContext.get_session() as session:
        yield session
```

```python
# src/api/dependencies/services.py
import logging
from fastapi import Depends, Request
from sqlmodel import Session
from .database import get_db_session
from shared.services.core.build_service import BuildService
from shared.services.core.deployment_service import DeploymentService
# ... import all services

def get_logger(request: Request) -> logging.Logger:
    """Extract logger from request state (set by ApiMiddleware)."""
    return request.state.logger

def get_build_service(
    logger: logging.Logger = Depends(get_logger),
    session: Session = Depends(get_db_session),
) -> BuildService:
    return BuildService(logger, session)

def get_deployment_service(
    logger: logging.Logger = Depends(get_logger),
    session: Session = Depends(get_db_session),
) -> DeploymentService:
    return DeploymentService(logger, session)

# ... one function per service
```

```python
# src/api/dependencies/auth.py
import logging
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session
from shared.dtos.core.auth_dtos import SafeUserDTO
from shared.services.core.auth_service import AuthService
from .database import get_db_session
from .services import get_logger

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    logger: logging.Logger = Depends(get_logger),
    session: Session = Depends(get_db_session),
) -> SafeUserDTO:
    session_id = credentials.credentials
    auth_service = AuthService(logger, session)
    return auth_service.validate_session(session_id)
```

### Routers: Import Dependencies, Don't Define Them

Routers import dependency functions from `src/api/dependencies/` and use them with `Depends()`. They never create services directly and never define `_get_service()` functions:

```python
# src/api/routers/private_builds_router.py
from api.dependencies.auth import get_current_user
from api.dependencies.services import get_build_service

router = APIRouter()

@router.get("")
def list_builds(
    current_user: dict = Depends(get_current_user),
    service: BuildService = Depends(get_build_service),
) -> BuildListResponseDTO:
    return service.list_builds()
```

## Service Constructor Pattern

**Every service takes `logger` as the first constructor argument**, followed by `session`:

```python
import logging
from sqlmodel import Session

class BuildService:
    def __init__(self, logger: logging.Logger, session: Session) -> None:
        self.logger = logger
        self.session = session
        self.build_repo = BuildRepository(session)
```

For services where session is optional (e.g. `ConfigSyncService`):

```python
class ConfigSyncService:
    def __init__(self, logger: logging.Logger, session: Optional[Session] = None) -> None:
        self.logger = logger
        self.session = session
```

Services use `self.logger` for any logging they need. They do NOT create their own loggers.

## Worker Logging Pattern

### Logger initialization (`src/worker/main.py`)

```python
from shared.logging import get_file_logger, set_transaction_id

logger = get_file_logger("worker", force_reconfigure=True)
logger.setLevel(log_level)  # INFO in production, DEBUG in development
```

### Transaction IDs per job

The worker sets a transaction ID before processing each build/deployment and passes logger to processors:

```python
set_transaction_id(f"build-{build.id}")
try:
    process_build(session, build, logger)
finally:
    set_transaction_id("")
```

### Processors receive the logger as argument

Worker processors receive the logger as an argument from `main.py` and pass it to all services:

```python
# src/worker/build_processor.py
def process_build(session: Session, build: Build, logger: logging.Logger) -> None:
    build_service = BuildService(logger, session)
    metadata_service = BuildMetadataService(logger, session)
    config_sync_service = ConfigSyncService(logger, session)
    # ...
```

```python
# src/worker/deploy_processor.py
def process_deployment(session: Session, deployment: Deployment, logger: logging.Logger) -> None:
    deployment_service = DeploymentService(logger, session)
    # ...
```

### Per-job log files (build/deploy logs)

Separate from the worker logger, each build/deployment writes detailed output to its own log file using `TimestampedLogFile` from `worker/common.py`:

```python
from worker.common import append_to_log, run_script

# Append timestamped text to a per-build log file
append_to_log(log_file_path, "Build started\n")

# Run a subprocess with output captured to the log file
exit_code = run_script(command, work_dir, log_file_path, "Running build")
```

These per-job logs go to `{DATA_DIR}/build-logs/{build_id}.log` and `{DATA_DIR}/deploy-logs/`.

## Infrastructure

### Systemd Service Templates

#### API Service (`mcc/mcc-pipeline.service`)
```ini
[Service]
User=www-data
Group=www-data
WorkingDirectory={{API_SYMLINK}}
Environment="ENV_TYPE=production"
Environment="LOG_ROOT={{REMOTE_BASE}}/logs"
Environment="DATA_DIR={{DATA_DIR}}"
ExecStart={{REMOTE_BASE}}/.venv/bin/gunicorn api.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:{{API_PORT}} \
    --access-logfile {{REMOTE_BASE}}/logs/access-gunicorn.log \
    --error-logfile {{REMOTE_BASE}}/logs/error-gunicorn.log
```

#### Worker Service (`mcc/mcc-pipeline-worker.service`)
```ini
[Service]
User=stenvala
Group=stenvala
WorkingDirectory={{API_SYMLINK}}
Environment="ENV_TYPE=production"
Environment="LOG_ROOT={{REMOTE_BASE}}/logs"
Environment="DATA_DIR={{DATA_DIR}}"
ExecStart={{REMOTE_BASE}}/.venv/bin/python -m worker.main
```

### Remote Directory Setup & Permissions

During deployment (`mcc/deploy_api.py` `setup_api_permissions`):
```python
c.run(f"mkdir -p {remote_base}/logs")
c.run(f"sudo chown {dir_user}:{dir_group} {remote_base}/logs")
c.run(f"sudo chmod g+rw {remote_base}/logs")
```

The logs directory is owned by `www-data:stenvala` (DIR_USER:DIR_GROUP from conf.yml), which allows:
- The API service (runs as `www-data`) to write `api.log`, gunicorn logs
- The worker service (runs as `stenvala`) to write `worker.log`
- Nginx (runs as `www-data`, root for error log) to write nginx logs

### Service Users

| Service | User | Group | Configured in |
|---------|------|-------|---------------|
| API (gunicorn) | `www-data` | `www-data` | `mcc/mcc-pipeline.service` |
| Worker | `stenvala` | `stenvala` | `mcc/mcc-pipeline-worker.service` |
| Nginx | `www-data` | root (for error log) | System default |

### Nginx Logs (Remote Only)

Configured in the nginx site config (`mcc/{domain}` or generated by `deploy_server.py`):
```nginx
access_log {REMOTE_BASE}/logs/access-nginx.log;
error_log {REMOTE_BASE}/logs/error-nginx.log;
```

No built-in rotation; relies on system logrotate.

## Summary: When to use what

| Context | Logger source | Transaction ID | Error handling |
|---------|--------------|----------------|----------------|
| API middleware | `get_file_logger("api")` + `StructuredLogger` | `set_transaction_id(request_id)` per request | Middleware catches all |
| API dependency injectors | `request.state.logger` (set by middleware) | Inherited from middleware | Let exceptions bubble |
| API services | `self.logger` (injected via constructor) | Inherited from middleware | Let exceptions bubble |
| API routers | No direct logging | Inherited from middleware | Let exceptions bubble |
| Worker main loop | `get_file_logger("worker")` | `set_transaction_id(f"build-{id}")` per job | Caught in `_poll_once` |
| Worker processors | `logger` argument from `main.py` | Inherited from main loop | Let exceptions bubble |
| Services (both contexts) | `self.logger` (injected via constructor) | Inherited from caller | Use `self.logger` |
| Per-job output | `append_to_log()` / `run_script()` | N/A (separate file) | Written to `{DATA_DIR}` |

## Troubleshooting

### Diagnose locally
```python
from shared.logging import diagnose_logging
diagnose_logging()
```

### Check remote logs
```bash
# Via systemd journal
sudo journalctl -u mcc-pipeline.service -n 50 --no-pager
sudo journalctl -u mcc-pipeline-worker.service -n 50 --no-pager

# Direct log files
tail -f {REMOTE_BASE}/logs/api.log
tail -f {REMOTE_BASE}/logs/worker.log
```

### Common issues
- **Permission denied writing logs**: Ensure logs dir is `chown {DIR_USER}:{DIR_GROUP}` with `chmod g+rw`
- **Gunicorn workers don't log**: Missing `reinit_logging_on_worker_start` hook causes stale file handles after fork
- **Logs go to stdout instead of file**: `LOG_ROOT` not set or directory not writable; `get_file_logger` falls back to console with a stderr warning
