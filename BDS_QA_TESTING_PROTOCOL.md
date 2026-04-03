# Boswell Digital Solutions — QA Testing Protocol

> Repeatable 8-tier testing methodology for all BDS applications.
> Derived from the AuthorForge v1.0 testing campaign (Feb 2026).
> Load alongside `BDS_VSCODE_CLAUDE_SOP.md` for any project entering QA.

**Version:** 1.2 (2026-02-17)  
**Owner:** Boswell Digital Solutions LLC  
**Applies to:** All Forge ecosystem applications and future BDS projects  
**Companion docs:** `BDS_VSCODE_CLAUDE_SOP.md` (development standards), BugCheck schemas (finding, enrichment, lifecycle event, run report)

---

## 1. Purpose & Philosophy

This protocol defines how BDS applications are tested from infrastructure through accessibility. It is designed to be applied to any project in the Forge ecosystem — AuthorForge, TradeForge, or any future application — by following the same sequence, adapting the specifics to each project's stack and module set.

### Core Principles

| Principle | Meaning |
|-----------|---------|
| **Fail-closed** | Every unknown state, missing config, or corrupt data produces a visible error — never a silent failure or empty div |
| **User agency** | No test should validate a path where the user is locked out of their data |
| **Offline-first** | Every feature must work without network access. Cloud-dependent paths are tested separately and clearly gated |
| **BugCheck compliance** | All findings follow `finding.schema.json` with severity S0–S4 and structured enrichment |
| **Spec-first testing** | The test plan is generated from `SYSTEM.md`, not from reading code. Tests validate the contract, not the implementation |
| **Tier gates** | Each tier requires ≥ 95% pass rate with zero S0/S1 findings before proceeding to the next |

### Severity Definitions (BugCheck Standard)

| Level | Meaning | Response SLA | Gate Impact |
|-------|---------|-------------|-------------|
| S0 | Catastrophic — data loss, crash, security breach | Fix before any release | Blocks all tiers |
| S1 | Critical — feature completely broken, no workaround | Fix before beta | Blocks current tier |
| S2 | Major — feature degraded but workaround exists | Fix before v1.0 | Logged, does not block |
| S3 | Minor — cosmetic, polish, edge case | Fix when possible | Logged only |
| S4 | Enhancement — suggestion, not a defect | Backlog | Logged only |

---

## 2. Protocol Overview: The 5-Phase QA Lifecycle

Every BDS application follows this lifecycle when entering QA:

```
Phase 1: PLAN  ──── Generate test plan from SYSTEM.md
    ↓
Phase 2: AUDIT ──── Review plan against spec (find gaps, inaccuracies)
    ↓
Phase 3: INFRA ──── Execute T0 pre-flight (resolve blockers before testing)
    ↓
Phase 4: BUILD ──── Implement tests tier-by-tier (T1 → T8)
    ↓
Phase 5: GATE  ──── Evaluate Definition of Done, produce release report
```

Each phase has explicit entry criteria, deliverables, and exit criteria documented below.

---

## 3. Phase 1: PLAN — Generate the Test Plan

### Entry Criteria

- `SYSTEM.md` exists and is current (all modules, routes, tables, components documented)
- Architecture spec exists with module list and dependency graph
- BugCheck schemas are available in the project

### Process

**Step 1: Inventory the application surface.**

Read `SYSTEM.md` systematically and extract:

| Category | What to Count | Example |
|----------|---------------|---------|
| Services | Every process that must be running | PostgreSQL, API, Backend, Sync Server |
| Database tables | Every table, its owner, migration system | 74 tables across 2 migration systems |
| API routes | Every HTTP endpoint by service | 85 Fastify routes, 12 Python routes |
| Frontend components | Every Svelte/React component file | MapCanvas, Smithy, CollabPanel |
| Frontend utilities | Every pure function module | geometry.ts, pathfinding.ts, spine.ts |
| Store/state modules | Every reactive state container | Focus Veil, collab stores, settings |
| Cross-module flows | Every integration point between modules | Lore ↔ Map entity linking, Guard ↔ RAG |
| External integrations | Every third-party dependency | OpenAI, IngramSpark specs, Stripe |

**Step 2: Map the inventory to 8 test tiers.**

Every BDS test plan uses this exact tier structure:

| Tier | Name | Scope | Typical Tooling |
|------|------|-------|-----------------|
| T0 | Infrastructure Pre-Flight | Services boot, DB schema, env vars, cross-service proxies | Bash, curl, psql |
| T1 | Unit Tests | Pure functions, utilities, stores — no DOM, no network | Vitest / pytest |
| T2 | Component Tests | UI components rendered in isolation with mocked data | @testing-library + Vitest |
| T3 | API Contract Tests | Request/response shape validation for every route | supertest / httpx |
| T4 | Integration Tests | Multi-module browser flows | Playwright |
| T5 | E2E User Journeys | Full workflows from start to finish | Playwright |
| T6 | Performance & Load | Render budgets, response times, large data stress | Lighthouse, custom benchmarks |
| T7 | Platform & Packaging | Desktop builds, sidecar bundling, CI matrix | Platform-specific CI |
| T8 | Accessibility | WCAG 2.1 AA, keyboard nav, screen reader | axe-core, manual audit |

**Step 3: Write the test plan document.**

The test plan is a Markdown file named `{APP}_COMPREHENSIVE_TEST_PLAN.md`. It must include:

1. Testing philosophy and guiding principles
2. Tier overview table with planned test counts
3. Detailed checks/tests per tier with specific assertions
4. E2E journey scenarios (minimum 5 user journeys)
5. Performance benchmarks with measurable targets
6. Test data strategy (seed script, fixtures, cleanup)
7. Tooling setup checklist
8. Definition of Done for release readiness
9. BugCheck run report template
10. Regression smoke suite specification

### Exit Criteria

- Test plan document exists with all 10 sections
- Every module, route, table, and component from SYSTEM.md appears in at least one tier
- Test count totals are realistic (typically 500–1000 for a full application)

---

## 4. Phase 2: AUDIT — Review Plan Against Spec

### Entry Criteria

- Test plan document exists (Phase 1 complete)
- `SYSTEM.md` is the current version

### Process

Perform a line-by-line comparison of `SYSTEM.md` against the test plan. Check for:

| Check | What to Look For |
|-------|-----------------|
| **Missing coverage** | Routes, tables, components, or features in SYSTEM.md not mentioned in any tier |
| **Wrong names** | Table names, column names, route paths that don't match the spec exactly |
| **Ownership conflicts** | Tables or resources claimed by multiple services or migration systems |
| **Missing unit tests** | Pure function modules with no T1 entry (especially math-critical functions) |
| **Missing contract tests** | Route groups with no T3 entry (especially CRUD groups) |
| **Missing security tests** | Permission enforcement, token validation, role-based access not tested |
| **Missing failure modes** | No tests for service-down, corrupt data, expired tokens, network disconnect |
| **Performance gaps** | Features with response time requirements but no T6 benchmark |
| **Documentation debt** | Features that exist in code but aren't in SYSTEM.md (or vice versa) |

**Produce a numbered findings list** with severity classification. Every finding must state:
- What's missing or wrong
- Which tier it affects
- The specific fix to apply to the test plan

### Exit Criteria

- Audit findings document exists
- All findings have been applied to the test plan (version incremented)
- Net test count change is documented

---

## 5. Phase 3: INFRA — T0 Infrastructure Pre-Flight

### Entry Criteria

- Audited test plan exists (Phase 2 complete)
- Development environment is available

### Why T0 Exists

T0 catches infrastructure blockers before they waste testing time. In the AuthorForge campaign, T0 discovered:

- A stale process running for 5 days with unapplied migrations
- A missing environment variable that prevented service startup
- A rogue migration file with 6 unused columns causing schema conflicts
- A dual migration system (Alembic + pg-migrate-forge) with table ownership violations

Every one of these would have caused cascading test failures in T1–T5 if not caught first.

### Required T0 Checks (Adapt Per Project)

#### 5.1 Service Boot Checks

For every service in the stack:

| Check | Verification |
|-------|-------------|
| Service responds on expected port | `curl http://localhost:{port}/health` → 200 |
| Health endpoint includes version/migration info | Response body contains schema version, pending count |
| Cross-service proxies work | Request to proxy service returns upstream data |
| All services start from cold (Docker/fresh) | `docker-compose up` → all healthy within timeout |

#### 5.2 Database Schema Checks

| Check | Verification |
|-------|-------------|
| All migrations apply cleanly on fresh DB | Each migration system runs to head with zero errors |
| Migrations are reversible | Downgrade one step, re-upgrade — no data loss |
| Multiple migration systems coexist | Tracking tables for each system present, no conflicts |
| FK cascades correct | DELETE parent → all children cleaned up |
| Indexes present on FK columns | Query `pg_indexes` for every FK column |
| Enum constraints enforced | INSERT invalid enum value → rejected at DB level |
| Every documented table exists | Cross-reference SYSTEM.md §11 against `\dt` |
| **Migration table ordering correct** | Tables with FK dependencies are created after their referenced tables within the same migration (see §5.2.1) |
| **Enum types are idempotent** | `CREATE TYPE` statements use `IF NOT EXISTS` wrappers or `checkfirst=True` (see §5.2.2) |
| **Migrations apply on non-fresh DB** | Run `upgrade head` against a DB already at head — zero errors (catches non-idempotent DDL) |
| **Migration transaction isolation** | A single failed DDL statement does not poison the entire migration transaction, leaving the DB in an unrecoverable state without manual intervention |

##### 5.2.1 Migration Table Ordering Validation

**Background:** When Alembic (or any migration tool) creates multiple tables in a single migration, FK constraints require that referenced tables exist before referencing tables. If table B has `FOREIGN KEY(x) REFERENCES table_a(id)`, then table A must be created first. Alembic's autogenerate usually resolves this, but can fail when:

- Circular FK relationships exist (A references B, B references A)
- Models are imported in an order that doesn't match the dependency graph
- Manually written migrations list tables in arbitrary order

**Verification procedure:**

1. Extract every `op.create_table()` call from each migration file
2. For each table, list its FK references
3. Verify that every referenced table is either created earlier in the same migration or exists from a previous migration
4. If violations are found, reorder the `op.create_table()` calls or split into separate migrations

**Automated check (Alembic/PostgreSQL):**

```bash
# Apply migrations against a truly empty database — not one with leftover objects
dropdb --if-exists test_migration_ordering && createdb test_migration_ordering
cd ecosystem/DataForge && DATABASE_URL="postgresql://localhost/test_migration_ordering" alembic upgrade head
echo $?  # Must be 0
```

##### 5.2.2 Enum and Named Type Idempotency

**Background:** PostgreSQL `CREATE TYPE ... AS ENUM` fails if the type already exists. When a migration that creates an enum fails partway through (e.g., due to a table ordering bug), the enum may have been created successfully before the transaction was rolled back — but PostgreSQL does not roll back DDL in all contexts. Re-running the migration then fails on the enum creation, producing the misleading `InFailedSqlTransaction` error.

**Required pattern (all three parts are mandatory):**

SQLAlchemy has three independent paths that can trigger `CREATE TYPE` for an enum. All three must be suppressed for idempotent migrations. This was validated through 6 deploy attempts on AuthorForge (AF-T0-003) before arriving at this complete pattern.

```python
import sqlalchemy as sa
from alembic import op

def upgrade():
    conn = op.get_bind()

    # ── STEP 1: Create enums via DO blocks (idempotent) ──
    # PostgreSQL exception handling skips creation if type already exists.
    # This is the ONLY place enum creation should happen.
    conn.execute(sa.text("""
        DO $$ BEGIN
            CREATE TYPE scenestatus AS ENUM ('blank', 'draft', 'revision', 'final');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """))
    conn.execute(sa.text("""
        DO $$ BEGIN
            CREATE TYPE entitykind AS ENUM ('character', 'location', 'artifact',
                'magic_rule', 'event', 'faction', 'creature', 'theme');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """))
    # ... repeat for all app enums ...

    # ── STEP 2: Define Enum objects with BOTH safety flags ──
    # create_type=False    → prevents auto-creation during op.create_table()
    # metadata=sa.MetaData() → isolates enum from table metadata graph,
    #                          prevents _on_table_create event from firing
    # Without BOTH flags, SQLAlchemy bypasses Step 1 and tries to
    # CREATE TYPE itself — without any idempotency guard.
    scene_status = sa.Enum('blank', 'draft', 'revision', 'final',
                           name='scenestatus',
                           create_type=False,        # ← suppress auto-creation
                           metadata=sa.MetaData())   # ← isolate from table events

    entity_kind = sa.Enum('character', 'location', 'artifact', 'magic_rule',
                          'event', 'faction', 'creature', 'theme',
                          name='entitykind',
                          create_type=False,
                          metadata=sa.MetaData())

    # ── STEP 3: Create tables — enums already exist, correct FK order ──
    op.create_table('scenes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('status', scene_status),
        # ...
    )
    op.create_table('lore_entities',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('kind', entity_kind),
        # ...
    )
    # Tables with FK dependencies come AFTER their referenced tables
    op.create_table('beats',
        sa.Column('scene_id', sa.Integer(), sa.ForeignKey('scenes.id')),
        # ...
    )
```

**Why all three parts are required:**

| Flag | What it prevents | What happens without it |
|------|-----------------|------------------------|
| `DO $$ BEGIN ... EXCEPTION` | Failure on re-deploy when enum already exists from a prior failed attempt | `DuplicateObject: type "X" already exists` |
| `create_type=False` | SQLAlchemy auto-creating the enum during `op.create_table()` | Bypasses your DO block; `CREATE TYPE` fires without idempotency guard |
| `metadata=sa.MetaData()` | SQLAlchemy's `_on_table_create` event walking the metadata graph and finding the enum | Even with `create_type=False`, some binding contexts still trigger auto-creation via event hooks |

**Incomplete patterns that were tried and failed (AuthorForge AF-T0-003):**

| Attempt | Pattern | Failure Mode |
|---------|---------|-------------|
| DO blocks only | `op.execute(DO $$...)` then `sa.Enum(name='...')` | SQLAlchemy bypasses DO block, fires `CREATE TYPE` via `_on_table_create` event |
| Event listeners | `@event.listens_for` to intercept `before_create` | Incompatible with SQLAlchemy 2.0 Alembic context |
| SAVEPOINT isolation | `conn.begin_nested()` around `op.create_table()` | Table creation fails inside savepoint when enum event fires; table never created; FK from downstream table fails |
| Enum-first + `create_type=False` | `safe_create_enum()` then `sa.Enum(create_type=False)` | `_on_table_create` event still fires via metadata graph traversal |
| **DO blocks + `create_type=False` + `metadata=sa.MetaData()`** | **All three suppression paths covered** | **✅ Works on fresh and existing databases** |

```sql
-- Raw SQL migrations — always guard named types
DO $$ BEGIN
    CREATE TYPE scenestatus AS ENUM ('blank', 'draft', 'revision', 'final');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
```

**Verification:** After all migrations apply cleanly, run `upgrade head` a second time — it must produce zero errors.

#### 5.3 Environment & Config Checks

| Check | Verification |
|-------|-------------|
| All required env vars have defaults or docs | Audit `.env.example` against service startup |
| No hardcoded secrets in source | `grep -r "sk-" --include="*.ts" --include="*.py"` → zero |
| CORS configured correctly | Allowed origins match deployment modes |
| CSP headers correct (desktop apps) | Config allows required connections |

#### 5.4 Deployment Platform Pre-Flight

**Why this exists:** Migrations that pass locally can fail on deployment platforms (Render, Railway, Fly.io) because the deployment DB has different state — leftover objects from failed deploys, different PostgreSQL versions, or schema drift from manual hotfixes. The AuthorForge v1.0 campaign discovered this when a Render deploy failed because a table ordering bug in Alembic caused a `FOREIGN KEY ... REFERENCES scenes` to execute before the `scenes` table was created. The resulting aborted transaction then cascaded into every subsequent DDL statement in the migration, producing misleading `InFailedSqlTransaction` errors.

| Check | Verification |
|-------|-------------|
| Migrations apply against a clone of production DB | `pg_dump` production → restore to local → run `upgrade head` → zero errors |
| Migrations apply against a truly empty DB | `dropdb && createdb` → run `upgrade head` → zero errors |
| No orphaned types/sequences from failed deploys | `SELECT typname FROM pg_type WHERE typname IN ({app_enums})` — if types exist but tables don't, manual cleanup is needed |
| Build command runs migrations before app start | Verify the platform's build/start script runs migrations as a discrete step with clear error handling |
| Migration failure produces clear exit code | A failed migration must exit non-zero — not swallow the error and start the app with an inconsistent schema |
| Transaction isolation strategy is documented | Document whether migrations run in a single transaction (Alembic default) or per-statement, and the implications for partial failure recovery |

**Deployment migration recovery checklist (when a deploy fails on migration):**

1. **Read the full log from the top** — the first error is the root cause; subsequent errors are transaction poisoning
2. **Check for orphaned DB objects** — `\dT` (types), `\dt` (tables), `\di` (indexes) on the deployment DB
3. **If orphaned objects exist** — clean them up manually before re-deploying:
   ```sql
   -- Example: remove orphaned enum from a failed migration
   DROP TYPE IF EXISTS entitykind;
   -- Example: remove partially-created table
   DROP TABLE IF EXISTS beats;
   ```
4. **Fix the migration** — apply the idempotency patterns from §5.2.2 and table ordering fixes from §5.2.1
5. **Test locally against a fresh DB** before re-deploying
6. **Consider stamping** — if the DB is in a known-good state but Alembic's version tracker is wrong: `alembic stamp head`

### Testing Modes

**Critical concept:** Not all services may be available locally. Define testing modes up front:

| Mode | When to Use | What's Available |
|------|-------------|------------------|
| **Mode A (Monorepo)** | External services unavailable | Local DB + monorepo services only |
| **Mode B (Full Stack)** | All services running (Docker/staging) | Complete stack including external services |

**Mode A is sufficient for T0 (partial), T1, T2, T3 (proxy routes return expected errors), T6, T7, T8.**
**Mode B is required for T4, T5, and full T3 validation.**

Document which checks require Mode A vs Mode B. Never block testing entirely because one external service is unavailable.

### T0 Findings Log

Maintain a running findings table in the test plan:

| ID | Severity | Title | Status | Resolution |
|----|----------|-------|--------|------------|
| {APP}-T0-001 | S1 | Description | ✅/⏸️/🔴 | What was done |

**Every T0 finding must be resolved or explicitly deferred with documented rationale before proceeding to T1.**

### Exit Criteria

- All T0 checks executed (Mode A minimum)
- Zero S0/S1 findings unresolved
- Findings log is complete and committed to test plan
- Testing mode declared for remaining tiers

---

## 6. Phase 4: BUILD — Implement Tests Tier by Tier

### Entry Criteria

- T0 pre-flight complete (Phase 3)
- Testing mode declared
- Test tooling installed and configured

### Implementation Order

**Always implement in this order.** Each tier validates the foundation the next tier depends on.

```
T1 (Unit) → T2 (Component) → T3 (API Contract) → T4 (Integration) → T5 (E2E) → T6 (Perf) → T7 (Platform) → T8 (A11y)
```

### 6.1 T1 — Unit Tests: The 80/20 Strategy

**Key lesson from AuthorForge:** You cannot implement all planned unit tests in a single pass. Use the 80/20 rule — identify the P0 pure functions that protect the highest-consequence calculations and implement those first.

**Priority classification for T1:**

| Priority | Criteria | Example |
|----------|----------|---------|
| P0 — Implement first | Wrong answer causes user-visible failure or data loss | Spine width formulas, pathfinding, export formatting |
| P1 — Implement second | Wrong answer causes incorrect UI state | Focus Veil tiers, era filtering, permission helpers |
| P2 — Backlog | Wrong answer causes cosmetic issues | Toast dedup, telemetry span creation |

**T1 implementation guidelines:**

- **Pure functions first.** No mocks, no DOM, no network. These are the fastest to write and most stable.
- **State modules second.** Svelte 5 runes stores, React context — test the reactive logic with minimal mocking.
- **Utility wrappers third.** Platform detection, localStorage wrappers, API client URL construction.
- **Target: sub-1ms per test, zero flakiness.**

### 6.2 T2 — Component Tests: Infrastructure Before Tests

**Key lesson from AuthorForge:** Component test infrastructure setup is harder than writing the tests themselves. Budget time for framework configuration before writing a single assertion.

**Framework configuration checklist (Svelte 5 + Vitest):**

```typescript
// vitest.config.ts — CRITICAL for Svelte 5 runes
resolve: {
  conditions: ['browser'], // Forces browser builds for $state/$derived/$effect
},
```

**Component test stability rules:**

| Rule | Rationale |
|------|-----------|
| Use `data-testid` attributes, not CSS selectors | Class names change with styling; test IDs are stable by convention |
| Mock API calls at the fetch level | Don't mock internal functions — mock the boundary |
| Test render output, not implementation | Assert "node appears at (100, 200)" not "setState was called" |
| Limit to critical UI components | Smithy editor, primary canvas, core navigation — not every button |

**Component priority order:**

1. The core product component (editor, canvas, main workspace)
2. The most complex component (highest regression risk)
3. UX differentiators (features unique to this product)
4. Error-path components (toast, error boundaries)
5. Navigation/layout (shell, sidebar, routing)

### 6.3 T3 — API Contract Tests: Mock the Boundary

**Key lesson from AuthorForge:** API contract tests should pass regardless of whether upstream services are running. Mock at the fetch boundary.

**Contract test pattern:**

```typescript
// Mock fetch globally — every T3 test controls its own responses
vi.stubGlobal('fetch', vi.fn());

test('POST /map/nodes creates node via DataForge proxy', async () => {
  fetch.mockResolvedValueOnce(new Response(JSON.stringify({ id: 1, name: 'Rivendell' }), {
    status: 201, headers: { 'Content-Type': 'application/json' }
  }));

  const res = await app.inject({ method: 'POST', url: '/map/nodes/project/1', payload: { name: 'Rivendell' } });

  expect(res.statusCode).toBe(201);
  expect(JSON.parse(res.body)).toHaveProperty('name', 'Rivendell');
});
```

**T3 coverage targets:**

| Route Group | Minimum Tests |
|-------------|---------------|
| Each CRUD resource | 4 (create, read, update, delete) |
| Each proxy route | 2 (success passthrough, upstream error propagation) |
| Each validation route | 2 (valid input, invalid input → 400) |
| Error contract | 1 per expected error code (400, 404, 409, 413, 502, 503) |

### 6.4 T4/T5 — Integration & E2E: Mode B Required

These tiers require the full stack. Define minimum 5 user journeys that exercise the primary workflows:

| Journey | Coverage |
|---------|----------|
| Journey 1 | Create → edit → save → export (the core product loop) |
| Journey 2 | Import existing data → transform → export (migration path) |
| Journey 3 | Multi-entity management (series, collections, linked data) |
| Journey 4 | Collaboration/sharing flow (if applicable) |
| Journey 5 | Most complex module end-to-end (map, canvas, dashboard) |

Additional journeys for crash recovery, failure modes, and edge cases as needed.

### 6.5 T6 — Performance Benchmarks

Define measurable targets for every performance-sensitive operation. Every target must have:

- A numeric threshold (e.g., "< 200ms")
- A measurement method (e.g., "Lighthouse FCP", "performance.now() delta")
- A test scenario with defined data size (e.g., "100 nodes, 200 edges")

**Standard benchmark categories:**

| Category | What to Measure | Typical Targets |
|----------|----------------|-----------------|
| Frontend render | Component mount time, frame rate during interaction | < 200ms mount, < 16ms per frame (60fps) |
| API response | Round-trip for CRUD, proxy routes, AI routes | < 50ms CRUD, < 2s AI, < 15s export |
| Large data stress | Maximum data size before degradation | Define "War and Peace scale" equivalent for your domain |
| Concurrent operations | Multi-user or multi-process throughput | Define requests/second or updates/second |

### 6.6 T7 — Platform & Packaging

For desktop applications (Tauri, Electron):

| Check | Verification |
|-------|-------------|
| Build completes on all target platforms | CI matrix: macOS (aarch64), Windows (x86_64), Linux (x86_64) |
| Sidecar processes bundle and launch | Health check succeeds after sidecar startup |
| Native menu renders | Platform-appropriate menu items visible |
| IPC commands respond | Every Rust↔JS command returns expected data |
| Window constraints enforced | Min-size, centering, decorations |
| First-launch wizard triggers | SetupWizard appears on fresh install |
| Clean quit | All child processes terminated on exit |
| Web mode compatibility | Desktop-only components hidden in browser |

### 6.7 T8 — Accessibility

**Non-negotiable minimum:** zero critical/serious axe-core violations on any route.

| Check | Tool |
|-------|------|
| Automated scan on every route | axe-core via Playwright |
| Keyboard navigation (Tab, Enter, Escape, arrows) | Manual + Playwright |
| Screen reader announcements | VoiceOver (macOS), NVDA (Windows) |
| `prefers-reduced-motion` respected | OS setting disables all animations |
| Color independence | Information conveyed by shape/text, not color alone |
| Text resizable to 200% without overflow | Browser zoom test |
| ARIA labels on all interactive elements | axe-core + manual |

### Exit Criteria (Phase 4)

- All implemented tests pass at ≥ 95% per tier
- Zero S0/S1 findings unresolved
- Test files committed to repository
- Test execution time documented (target: < 3 seconds for T1–T3 combined)

---

## 7. Phase 5: GATE — Release Readiness Evaluation

### Entry Criteria

- All tiers implemented to target coverage
- All findings resolved or explicitly deferred with rationale

### Definition of Done Template

The application is **release-ready** when every item below is checked:

```markdown
- [ ] All T0 pre-flight checks pass
- [ ] T1–T3 pass rate ≥ 98% with zero S0/S1
- [ ] T4–T5 pass rate ≥ 95% with zero S0/S1
- [ ] All T6 performance targets met
- [ ] T7 builds succeed on all target platforms
- [ ] T8 accessibility: zero critical/serious axe-core violations
- [ ] Regression smoke suite runs < 10 minutes
- [ ] All BugCheck run reports archived
- [ ] No unresolved S0 or S1 findings across any tier
- [ ] SYSTEM.md reflects actual schema and API state (no documentation debt)
```

### Regression Smoke Suite

After all tiers are complete, extract a fast regression suite (~50 tests, < 10 minutes) that runs on every PR:

| Category | Tests | Time Budget |
|----------|-------|-------------|
| Infrastructure health | 5 | 30s |
| Critical unit tests (highest-consequence calculations) | 10 | 30s |
| API contract spot-checks (one per route group) | 10 | 60s |
| Playwright happy-path per module | 1 per route | 5min |
| Playwright Journey 1 (core product loop) | 5 | 2min |
| Accessibility axe scan (3 most complex routes) | 3 | 30s |
| Platform build (host platform only) | 1 | varies |

### Release Report

Produce a final BugCheck run report summarizing:

- Total tests executed across all tiers
- Pass rate per tier
- All findings with resolution status
- Performance benchmark results vs. targets
- Platform build results
- Accessibility audit results
- Open items deferred to next version (with rationale)

---

## 8. Lessons Learned (AuthorForge Campaign Reference)

These lessons were extracted from the AuthorForge v1.0 testing campaign and should be applied to all future BDS projects.

### 8.1 T0 Catches Real Blockers

T0 is not a formality. In AuthorForge, it discovered:

| Finding | Impact if Missed |
|---------|-----------------|
| Stale process with unapplied migrations | Every T3 test would have failed with schema errors |
| Missing `COLLAB_SECRET` env var | Fastify wouldn't start — all API tests blocked |
| Rogue migration with 6 unused columns | Schema conflict would cascade into T4/T5 failures |
| Schema ownership conflict (covers table) | Two migration systems fighting over the same table |

**Rule: Never skip T0. Never "fix it later." Resolve every S0/S1 before touching T1.**

### 8.2 Spec-First Finds What Code-First Misses

The test plan was generated from `SYSTEM.md`, not from reading code. The Phase 2 audit found 17 gaps — including entire route groups missing from the plan, wrong table names, and undocumented columns. These would never be caught by "write tests for what exists in the codebase" because the bugs were in what was *missing* from the codebase.

**Rule: Always generate the test plan from the spec, then audit the plan against the spec. The gap between spec and implementation is where the bugs live.**

### 8.3 External Services Need Mode A/B Strategy

Not all services will be available locally. In AuthorForge, DataForge and Sync Server were external microservices not in the monorepo. Instead of blocking all testing, we defined Mode A (monorepo-only) and Mode B (full stack), documented which tiers work in each mode, and proceeded with Mode A for T0–T3.

**Rule: Define testing modes up front. Never let an unavailable service block testing of available services. A proxy route returning 502 is itself a valid contract test.**

### 8.4 Pure Functions First, Always

Test implementation order matters. AuthorForge Day 1 implemented 48 pure function tests (map geometry, spine width formulas) — zero mocks, zero DOM, zero flakiness, sub-1ms per test. These protected the highest-consequence calculations and established patterns for all subsequent tests.

| Test Type | Setup Cost | Execution Speed | Flakiness Risk | Write First? |
|-----------|-----------|-----------------|----------------|--------------|
| Pure functions | None | < 1ms | Zero | ✅ Always |
| State modules | Minimal | ~8ms | Zero | ✅ Second |
| Components | Moderate | ~10ms | Low | Third |
| Integration (Playwright) | High | ~500ms | Medium | Last |

**Rule: Start with pure functions. If you can only write 48 tests, make them pure functions that protect math-critical calculations.**

### 8.5 Component Test Infrastructure Is the Hard Part

Writing component tests is straightforward. Getting the framework configured is not. AuthorForge required a specific Vitest configuration fix for Svelte 5 runes:

```typescript
// vitest.config.ts — CRITICAL for Svelte 5
resolve: {
  conditions: ['browser'], // Forces browser builds for $state/$derived/$effect
},
```

Without this, every component test failed with "mount() is not available on the server." Budget explicit time for framework configuration before writing assertions.

**Rule: Budget 30–60 minutes for component test infrastructure setup. Document the configuration fix in the test plan for future reference.**

### 8.6 Use `data-testid`, Not CSS Selectors

AuthorForge's MapCanvas tests initially failed because they used CSS class selectors (`.map-node.selected`, `.region-poly`) that didn't match the actual DOM. After switching to rendered attributes (`cx`, `cy`, child element presence), tests became stable. For new projects, use `data-testid` attributes from the start.

**Rule: Add `data-testid` attributes to testable UI elements. CSS selectors break on styling refactors; test IDs are stable by convention.**

### 8.7 The 80/20 Rule for Coverage

AuthorForge's test plan specified 820 tests. In 10 hours (~3 days), 103 tests were implemented — 12.5% of the plan — covering 100% of P0 critical paths. The key was prioritization: spine width formulas (publisher rejection risk), map geometry (travel calculator accuracy), Smithy editor mount (core product), MapCanvas rendering (most complex component).

**Rule: You will not implement all planned tests before v1.0. Identify the P0 tests (highest consequence of failure) and implement those first. 40 carefully chosen tests provide more value than 400 random ones.**

### 8.8 Migration Ownership Must Be Explicit

AuthorForge used two migration systems (Alembic for DataForge, pg-migrate-forge for Fastify) sharing one database. A rogue Fastify migration tried to create a `covers` table that DataForge already owned — with incompatible schemas. The fix was deleting the rogue migration and adding only the one column the frontend actually used.

**Rule: Document table ownership in SYSTEM.md with explicit "Owner" column. Every migration file must be listed in the documentation. Any undocumented migration file is an S1 finding.**

### 8.9 BugCheck Integration Is Not Optional

Every finding from T0 through T8 was logged with a BugCheck-compliant ID, severity, title, status, and resolution. This made it possible to track the 10 findings across the entire campaign, distinguish between infrastructure issues and production bugs, and produce a clear release report.

**Rule: Log findings from the first T0 check. Use the BugCheck schema from day one. Don't wait until T5 to start tracking issues.**

### 8.10 Migrations Must Be Deployment-Safe, Not Just Dev-Safe

AuthorForge's Alembic migrations passed locally for weeks. On the first Render deploy, the build failed with `sqlalchemy.exc.ProgrammingError: relation "scenes" does not exist` — the `beats` table had a FK to `scenes`, but `scenes` was created later in the same migration. This table ordering bug had been invisible locally because the dev DB already had all tables from prior runs. The initial failure then poisoned the PostgreSQL transaction, causing every subsequent DDL statement (including `CREATE TYPE entitykind`) to fail with the misleading `InFailedSqlTransaction` error — making the root cause extremely difficult to identify from the bottom of the stack trace.

Resolving this required 6 deploy attempts over the course of a single session (AF-T0-003, S0 severity). Each attempt uncovered a different SQLAlchemy behavior that bypassed the previous fix. The final working pattern required suppressing three independent auto-creation paths simultaneously (see §5.2.2).

**Four classes of deployment migration bugs discovered:**

| Bug Class | Symptom | Root Cause | Prevention |
|-----------|---------|------------|------------|
| **Table ordering** | `relation "X" does not exist` during `CREATE TABLE Y` | FK references a table not yet created in the same migration | Validate dependency order (§5.2.1); test against empty DB |
| **Non-idempotent DDL** | `type "X" already exists` on re-deploy | `CREATE TYPE` without `IF NOT EXISTS` guard; leftover objects from a previously failed deploy | Use `DO $$ BEGIN ... EXCEPTION WHEN duplicate_object` pattern (§5.2.2) |
| **Transaction poisoning** | `InFailedSqlTransaction: current transaction is aborted` | An earlier DDL statement failed, PostgreSQL aborted the transaction, all subsequent statements in the same transaction are rejected | Always read the full deploy log from the top — the first error is the root cause, not the last |
| **SQLAlchemy auto-creation bypass** | `DuplicateObject: type "X" already exists` even with manual creation and `create_type=False` | SQLAlchemy's `_on_table_create` event walks the metadata graph and fires `CREATE TYPE` via a path that ignores `create_type=False` | Must also set `metadata=sa.MetaData()` on every `sa.Enum` to isolate it from the table metadata graph (§5.2.2) |

**Rule: Every migration must pass against a truly empty database (`dropdb && createdb && upgrade head`), not just a dev database with leftover state. Add this check to T0 and to CI. The gap between "works on my machine" and "works on deploy" is where migration bugs live.**

**Rule: SQLAlchemy enum idempotency requires three flags, not one. `DO $$ BEGIN` for PostgreSQL-level safety, `create_type=False` for the explicit creation path, and `metadata=sa.MetaData()` for the event-driven creation path. Any two of three will fail in some deployment context. See §5.2.2 for the complete pattern and the five failed approaches that led to it.**

---

## 9. Templates & Checklists

### 9.1 Test Plan Document Template

Every BDS test plan follows this structure:

```markdown
# {App Name} — Comprehensive Test Plan

**Version:** 1.0
**Date:** {date}
**Owner:** Boswell Digital Solutions LLC
**Stack Under Test:** {stack components with ports}

## 1. Testing Philosophy
## 2. Test Tiers Overview (table with 8 tiers)
## 3. Tier 0 — Infrastructure Pre-Flight
   ### 3.1 Service Boot Checks
   ### 3.2 Environment & Config Checks
   ### 3.3 Database Schema Integrity
   ### 3.4 Tier 0 Findings Log
## 4. Tier 1 — Unit Tests
   ### 4.1 Frontend Utilities
   ### 4.2 Framework-Specific Extensions
   ### 4.3 Backend Services
   ### 4.4 Additional Services
## 5. Tier 2 — Component Tests
## 6. Tier 3 — API Contract Tests
## 7. Tier 4 — Integration Tests
## 8. Tier 5 — E2E User Journeys
## 9. Tier 6 — Performance Benchmarks
## 10. Tier 7 — Platform & Packaging
## 11. Tier 8 — Accessibility Audit
## 12. Test Execution Order
## 13. Regression Smoke Suite
## 14. BugCheck Run Report Template
## 15. Test Data Strategy
## 16. Tooling Setup Checklist
## 17. Definition of Done
## 18. Revision Log
```

### 9.2 Finding ID Convention

```
{APP}-T{tier}-{sequence}

Examples:
  AF-T0-001    AuthorForge, Tier 0, finding #1
  TF-T3-015    TradeForge, Tier 3, finding #15
```

### 9.3 BugCheck Run Report Template

```json
{
  "run_id": "{app}-test-{date}-{sequence}",
  "schema_version": "v1",
  "started_at": "{ISO 8601}",
  "finished_at": "{ISO 8601}",
  "status": "completed | failed",
  "tool_version": "{app}-qa/1.0",
  "testing_mode": "mode-a | mode-b",
  "findings": [],
  "events": [
    { "event_id": "evt-001", "at": "{ISO 8601}", "kind": "RUN_CREATED" },
    { "event_id": "evt-002", "at": "{ISO 8601}", "kind": "SCAN_STARTED" },
    { "event_id": "evt-003", "at": "{ISO 8601}", "kind": "SCAN_COMPLETED" }
  ],
  "summary": {
    "total_tests": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "pass_rate": "0%",
    "s0_count": 0,
    "s1_count": 0,
    "coverage_pct": "0%"
  }
}
```

### 9.4 New Project QA Onboarding Checklist

When a new BDS project enters QA, verify:

- [ ] `SYSTEM.md` exists and is current (all modules, routes, tables documented)
- [ ] `BDS_VSCODE_CLAUDE_SOP.md` loaded as foundational context
- [ ] `BDS_QA_TESTING_PROTOCOL.md` (this document) loaded as QA context
- [ ] BugCheck schemas available (`finding.schema.json`, `enrichment.schema.json`, etc.)
- [ ] Test plan generated from SYSTEM.md (Phase 1)
- [ ] Test plan audited against SYSTEM.md (Phase 2)
- [ ] Testing modes defined (Mode A/B) based on service availability
- [ ] T0 pre-flight executed and all S0/S1 resolved (Phase 3)
- [ ] Deployment migration pre-flight passed — migrations apply against empty DB and production clone (Phase 3, §5.4)
- [ ] Migration idempotency verified — `upgrade head` runs twice without error (Phase 3, §5.2.2)
- [ ] T1 P0 pure function tests implemented (Phase 4, Day 1)
- [ ] Component test infrastructure configured and proven (Phase 4, Day 2)
- [ ] Test results committed to repository
- [ ] BugCheck findings log started in test plan

---

## 10. Applying This Protocol to a New Project

### Step-by-Step Quickstart

**Time estimate: 2–3 days to reach Phase 4 (test implementation) for a typical BDS application.**

1. **Load context** — Open `BDS_VSCODE_CLAUDE_SOP.md` + `BDS_QA_TESTING_PROTOCOL.md` + the project's `SYSTEM.md`

2. **Phase 1 (2–4 hours)** — Generate test plan:
   - Inventory all services, tables, routes, components, utilities from SYSTEM.md
   - Map to 8 tiers using the template in §9.1
   - Write at least 5 E2E user journeys
   - Set performance targets with measurable thresholds
   - Define test data strategy (seed script + fixtures)

3. **Phase 2 (1–2 hours)** — Audit plan against spec:
   - Line-by-line comparison of SYSTEM.md vs test plan
   - Produce numbered findings list
   - Apply all fixes, increment plan version

4. **Phase 3 (1–3 hours)** — Execute T0:
   - Start all available services
   - Run every T0 check
   - **Run deployment migration pre-flight (§5.4): test migrations against empty DB and production clone**
   - Resolve S0/S1 findings before proceeding
   - Log all findings in the test plan
   - Declare testing mode (A or B)

5. **Phase 4, Day 1 (4 hours)** — Foundation tests:
   - Identify P0 pure functions (highest-consequence calculations)
   - Implement 20–50 unit tests, zero mocks
   - Target: 100% pass rate, < 1s execution

6. **Phase 4, Day 2 (4 hours)** — Component + contract tests:
   - Configure component test framework (budget 30–60 min for setup)
   - Implement 10 critical component tests
   - Implement 10 API contract tests with fetch mocking
   - Target: 100% pass rate, < 3s execution

7. **Phase 4, Day 3+ (ongoing)** — Expand coverage:
   - Fill remaining T1–T3 gaps
   - Set up Mode B for T4/T5 when external services available
   - T6 performance benchmarks
   - T7 platform builds
   - T8 accessibility audit

8. **Phase 5** — Evaluate Definition of Done, produce release report

### Adapting the 8 Tiers to Different Stacks

The tier structure is universal. The tooling adapts to the stack:

| Stack | T1/T2 | T3 | T4/T5 | T6 |
|-------|-------|-----|-------|-----|
| SvelteKit + Fastify | Vitest + @testing-library/svelte | supertest | Playwright | Lighthouse |
| React + Express | Jest + @testing-library/react | supertest | Cypress or Playwright | Lighthouse |
| Rust + Tauri | cargo test | reqwest | WebDriver | criterion |
| Python + FastAPI | pytest | httpx + pytest | Playwright | locust |
| Pure API (no frontend) | pytest / Jest | httpx / supertest | httpx scenarios | k6 or locust |

The methodology is the same regardless of tooling: spec-first plan generation, audit, T0 pre-flight, pure-functions-first implementation, 80/20 prioritization.

---

## 11. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.2 | 2026-02-17 | **Complete enum idempotency pattern.** Updated §5.2.2 with battle-tested three-part pattern (`DO $$ BEGIN` + `create_type=False` + `metadata=sa.MetaData()`) including the five failed approaches and why each was insufficient. Added fourth bug class (SQLAlchemy auto-creation bypass) to §8.10. Documented the full 6-attempt AF-T0-003 resolution journey as reference for future projects. |
| 1.1 | 2026-02-17 | **Deployment migration safety.** Added §5.2.1 (migration table ordering validation), §5.2.2 (enum/named type idempotency), §5.4 (deployment platform pre-flight with recovery checklist), §8.10 (lesson learned from AuthorForge Render deploy failure — table ordering, non-idempotent DDL, transaction poisoning). Updated onboarding checklist and quickstart with deployment migration checks. |
| 1.0 | 2026-02-17 | Initial protocol — extracted from AuthorForge v1.0 testing campaign. 5-phase QA lifecycle, 8-tier test structure, Mode A/B strategy, 9 lessons learned, templates and checklists. |