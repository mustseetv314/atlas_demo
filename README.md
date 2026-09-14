# Atlas

## Overview

Atlas is a deliberately simple internal IT asset inventory. It presents a server-rendered website and REST API from an on-premises AKS Kubernetes workload and stores inventory in an external on-premises Microsoft SQL Server database.

## Features

- Dashboard counts and five recently created assets
- Create, read, update, and delete workflows
- Server-side search by tag, name, owner, or location
- Environment and status filters
- JSON CRUD API and interactive Swagger documentation
- Independent process liveness and database-backed readiness checks
- Idempotent table and fictional seed-data initialization

## Current Architecture

```text
Corporate User -> On-Prem Kubernetes / AKS -> atlas-web Service
                         -> Atlas Deployment (2 pods) -> External SQL Server -> AtlasDb
```

The application pods contain FastAPI, Jinja2, Uvicorn, SQLAlchemy, and PyODBC. SQL Server does not run in the container or cluster. See [the architecture document](docs/architecture.md) for the current topology and request flow.

## Technology Stack

Python 3.12, FastAPI, Uvicorn, SQLAlchemy, PyODBC, Pydantic, Jinja2, HTML, CSS, vanilla JavaScript, Microsoft ODBC Driver 18, Docker, and plain Kubernetes manifests.

## Repository Structure

- `app/`: configuration, data access, routes, templates, and styles
- `tests/`: isolated tests using an in-memory database
- `k8s/`: Namespace, ConfigMap, Secret example, Deployment, and Service
- `scripts/`: PowerShell setup, run, and smoke-test commands
- `docs/architecture.md`: current runtime topology and request flow

## Configuration

All runtime configuration is supplied by environment variables. Copy `.env.example` to `.env` for development and replace its placeholder database password. `APP_NAME`, `APP_ENV`, `APP_HOST`, and `APP_PORT` configure the process. `DB_SERVER`, `DB_PORT`, `DB_NAME`, `DB_USERNAME`, `DB_PASSWORD`, `DB_DRIVER`, and `DB_TRUST_SERVER_CERTIFICATE` configure SQL connectivity. Never commit `.env` or real credentials.

## SQL Server Dependency

Atlas requires Microsoft SQL Server and the `AtlasDb` database. The login must be able to connect, create the `assets` table when absent, and read/write its rows. Worker nodes and pods require internal DNS and TCP connectivity to `DB_SERVER:DB_PORT`; the default SQL port is 1433. The server is not assumed to be publicly accessible. Startup creates the schema and inserts nine fictional records only when the table is empty; unique asset tags and transaction rollback make concurrent initialization safe.

## Local Development

Install Microsoft ODBC Driver 18 for SQL Server, configure an accessible SQL Server, then run from PowerShell:

```powershell
.\scripts\setup.ps1
# Edit .env with valid database settings
.\scripts\run.ps1
```

Open `http://localhost:8000`. Startup intentionally fails if the configured SQL Server cannot be initialized.

## Building the Container

```bash
docker build -t atlas:1.0.0 .
```

The Linux image installs Microsoft ODBC Driver 18 and runs as a non-root user.

## Running the Container

```bash
docker run --rm --env-file .env -p 8000:8000 atlas:1.0.0
```

The container must be able to resolve and connect to the configured external database host.

## Kubernetes Deployment

Create a protected `atlas-db-secret` from the example values, make the `atlas:1.0.0` image available to the cluster, and apply the plain manifests:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.example.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

`secret.example.yaml` is a template and must not be applied with placeholder values in an operating environment. The `ClusterIP` Service exposes `atlas-web:8000` inside Kubernetes. The surrounding on-premises platform handles corporate-user access.

## Health Checks

- `GET /health/live`: process-only liveness; does not query SQL Server
- `GET /health/ready`: runs `SELECT 1`; returns HTTP 503 when disconnected
- `GET /health`: general database-aware health response

## REST API

- `GET /api/info`
- `GET /api/assets` (optional `search`, `environment`, and `status_filter` query parameters)
- `GET /api/assets/{id}`
- `POST /api/assets`
- `PUT /api/assets/{id}`
- `DELETE /api/assets/{id}`

Swagger is served at `/docs`. Create and update payloads validate required lengths and controlled asset type, environment, and status values.

## Testing

```bash
pytest
```

Tests substitute an in-memory database and do not need SQL Server. Against a running configured instance, use `./scripts/test.ps1 -BaseUrl "http://localhost:8000"`.

## Troubleshooting

- A startup database exception usually indicates DNS, TCP/firewall, certificate, credentials, permissions, or ODBC driver configuration.
- HTTP 503 from readiness indicates the live process cannot complete its SQL connectivity query.
- Duplicate asset tags return HTTP 409 through the API and a validation message in the web UI.
- Inspect container logs on stdout/stderr; Atlas does not write primary logs to local files.

## Security Notes

Database credentials belong in the Kubernetes Secret; non-sensitive settings belong in the ConfigMap. SQLAlchemy parameterizes queries, Pydantic validates API input, Jinja2 auto-escapes HTML templates, and Atlas avoids logging secrets or connection strings. Authentication and authorization are intentionally simplified and not implemented for this internal demonstration workload.
