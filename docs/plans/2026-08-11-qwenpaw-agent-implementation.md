# QwenPaw Furniture Agent Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a secure QwenPaw skill layer to the existing furniture platform, finish the in-progress configuration import feature, harden deployment, and deliver a publicly verifiable build.

**Architecture:** Preserve the Django/React modular monolith. Add a narrow authenticated Agent Gateway with audit/idempotency/confirmation controls, and package QwenPaw skills as thin HTTP clients of that gateway and existing deterministic services.

**Tech Stack:** Python 3.11+, Django/DRF, PostgreSQL 16, React 18, TypeScript, Vite, nginx, Docker Compose, QwenPaw Skills, pytest.

---

### Task 1: Protect and verify the in-progress configuration work

**Files:**
- Modify: `backend/products/tests/test_config_dimension_mutation.py`
- Modify: `backend/products/tests/test_flexible_config_import.py`
- Verify: `backend/products/services.py`
- Verify: `backend/products/views.py`
- Verify: `frontend/src/pages/products/ProductFormPage.tsx`

**Steps:**
1. Add failing tests for referenced dimension key/option protection, force deletion, cycle rejection, Excel format detection, preview-before-confirm, and transactional replacement.
2. Run the focused tests with `DB_ENGINE=sqlite` and verify failures expose real gaps.
3. Make the smallest service/view corrections required.
4. Run all backend tests and `npm run build`.
5. Commit the reviewed configuration feature as a checkpoint.

### Task 2: Add Agent Gateway audit and API contract

**Files:**
- Create: `backend/agent_gateway/__init__.py`
- Create: `backend/agent_gateway/apps.py`
- Create: `backend/agent_gateway/models.py`
- Create: `backend/agent_gateway/serializers.py`
- Create: `backend/agent_gateway/services.py`
- Create: `backend/agent_gateway/views.py`
- Create: `backend/agent_gateway/urls.py`
- Create: `backend/agent_gateway/migrations/0001_initial.py`
- Create: `backend/agent_gateway/tests/test_capabilities.py`
- Create: `backend/agent_gateway/tests/test_audit.py`
- Modify: `backend/config/settings.py`
- Modify: `backend/config/urls.py`

**Steps:**
1. Write tests for authentication, capabilities discovery, audit redaction, request IDs, and module permission enforcement.
2. Implement `AgentActionAudit`, request context helpers, and the capabilities endpoint.
3. Verify anonymous access is rejected and authenticated calls are audited without secrets.
4. Run migrations/checks and focused tests.
5. Commit the gateway foundation.

### Task 3: Implement read-only Agent capabilities

**Files:**
- Create: `backend/agent_gateway/tests/test_catalog_tools.py`
- Modify: `backend/agent_gateway/serializers.py`
- Modify: `backend/agent_gateway/services.py`
- Modify: `backend/agent_gateway/views.py`
- Modify: `backend/agent_gateway/urls.py`

**Steps:**
1. Write tests for product search, exact product details, validated price calculation, document search, case search, pagination, and forbidden module access.
2. Reuse existing querysets, serializers, and `PriceCalculationService`; do not duplicate business rules.
3. Return compact, stable JSON designed for agent consumption plus Web deep links.
4. Run focused and full backend tests.
5. Commit read-only tools.

### Task 4: Implement safe quote and import workflows

**Files:**
- Create: `backend/agent_gateway/tests/test_quote_workflow.py`
- Create: `backend/agent_gateway/tests/test_import_workflow.py`
- Modify: `backend/agent_gateway/models.py`
- Modify: `backend/agent_gateway/serializers.py`
- Modify: `backend/agent_gateway/services.py`
- Modify: `backend/agent_gateway/views.py`

**Steps:**
1. Write tests for idempotent quote draft creation, server-side pricing, object ownership, preview tokens, one-time confirmation, expiry, replay rejection, and audit results.
2. Implement idempotency and signed confirmation services bound to user/action/input digest.
3. Route quote creation and Excel confirmation through existing transactional domain services.
4. Ensure no skill can publish/send a quote or mutate imports without explicit confirmation.
5. Run focused and full backend tests, then commit.

### Task 5: Package QwenPaw Skills

**Files:**
- Create: `paw/skills/furniture-system/SKILL.md`
- Create: `paw/skills/furniture-catalog/SKILL.md`
- Create: `paw/skills/furniture-product-config/SKILL.md`
- Create: `paw/skills/furniture-quotes/SKILL.md`
- Create: `paw/skills/furniture-import/SKILL.md`
- Create: `paw/skills/furniture-documents/SKILL.md`
- Create: `paw/shared/furniture_api.py`
- Create: `paw/tests/test_furniture_api.py`
- Create: `paw/README.md`

**Steps:**
1. Write mocked HTTP contract tests for auth headers, query encoding, JSON/file requests, idempotency, confirmation, timeout handling, and secret redaction.
2. Implement one dependency-free Python client with explicit subcommands and machine-readable JSON output.
3. Write narrow Skill instructions that require preview/confirmation and forbid local price calculation or direct database access.
4. Validate all SKILL.md front matter and run Paw tests.
5. Commit the reusable Skill pack.

### Task 6: Add frontend quality and performance guardrails

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/vite.config.ts`
- Modify: `frontend/package.json`
- Create: `frontend/src/test/setup.ts`
- Create: `frontend/src/components/__tests__/ProtectedRoute.test.tsx`

**Steps:**
1. Add Vitest and React Testing Library with a failing smoke test.
2. Lazy-load route pages and configure stable vendor chunking.
3. Build and verify the initial JavaScript chunk is materially smaller than the current 1.45 MB bundle.
4. Run unit tests and the production build.
5. Commit frontend guardrails.

### Task 7: Harden reproducible public deployment

**Files:**
- Modify: `docker-compose.yml`
- Create: `.env.example`
- Create: `paw/docker-compose.yml`
- Create: `paw/.env.example`
- Create: `scripts/smoke_public.ps1`
- Create: `docs/deployment.md`

**Steps:**
1. Add health checks, internal-only database exposure, explicit production settings, persistent volumes, and QwenPaw Console authentication configuration.
2. Add a smoke script for frontend, login method behavior, API authentication rejection, and Agent capabilities.
3. Run `docker compose config`, Django `check --deploy`, backend tests, Paw tests, and frontend build.
4. Deploy the application through the authenticated Zeabur project and configure public domains/environment variables without printing secrets.
5. Run public smoke tests and record the exact URL and deployment revision.

### Task 8: Final acceptance verification

**Files:**
- Create: `docs/acceptance-report.md`

**Steps:**
1. Exercise login, product search/detail/configuration/price, quote draft, Excel preview, permission denial, sharing, document/case lookup, and Agent capabilities.
2. Capture actual API results and browser screenshots without exposing credentials or customer data.
3. Run the complete automated test matrix one final time.
4. Document delivered scope, public URLs, deployment revision, operator setup, and any credential-only activation step for the QwenPaw model/channel.
5. Commit and push the verified branch.
