# Furniture Platform Agent Guide

## Architecture

- Keep the application as a modular monolith: React/Vite frontend, Django REST Framework backend, PostgreSQL database, and nginx/Docker Compose deployment.
- QwenPaw is an orchestration channel. Paw skills are thin clients of authenticated HTTP APIs; they must not access PostgreSQL or media volumes directly.
- Business invariants live in Django services. LLM output is untrusted input and must pass serializer, permission, and domain validation.

## Required Commands

Run backend tests without a local PostgreSQL service:

```powershell
$env:DB_ENGINE='sqlite'
python -m pytest -q
```

Run frontend verification:

```powershell
npm run build
```

Run Paw client tests:

```powershell
python -m pytest paw/tests -q
```

Run the production stack:

```powershell
docker compose up --build -d
```

## Business Invariants

- Never calculate a sell price in a prompt or Paw script. Always call `PriceCalculationService` through the backend API.
- Historical quote items are snapshots. Product or configuration changes must not rewrite historical quote descriptions or prices.
- Matrix pricing accepts only an exact valid configuration combination. Rule pricing starts with base price and applies validated deltas.
- Excel imports always follow parse/preview before confirm. A confirm operation must be transactional and reject files with errors or unresolved mappings.
- All reads and writes enforce the authenticated user's module permissions and object ownership.
- External shares enforce active state, password, expiration, and visit limits on the server.
- Agent write actions require an idempotency key and produce an audit record. Sensitive writes require a short-lived, one-time confirmation token.

## Change Discipline

- Work on a `codex/` branch or an isolated worktree; never let two agents edit the same worktree.
- Write a failing test before changing domain behavior.
- Do not edit generated migration files after they have shipped; create a new migration.
- Do not commit `.env`, model keys, Django tokens, customer documents, database dumps, or QwenPaw secret volumes.
- Preserve existing API response compatibility unless the implementation plan explicitly documents a versioned change.
- Before delivery, run the full backend suite, Paw tests, frontend production build, Django deployment checks, and public smoke tests.

## Deployment

- The public application is served through the frontend reverse proxy; PostgreSQL and the Django admin port must not be exposed directly.
- Production requires HTTPS, a non-default admin password, a generated Django secret, explicit allowed hosts/origins, persistent PostgreSQL/media volumes, and backups.
- QwenPaw Console authentication must be enabled whenever it is reachable outside localhost.
