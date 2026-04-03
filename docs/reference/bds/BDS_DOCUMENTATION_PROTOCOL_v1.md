# BDS Documentation Protocol

**Version:** 1.0 · February 2026  
**Status:** Active Standard  
**Scope:** All Forge Ecosystem Applications  
**Companion To:** `BDS_VSCODE_CLAUDE_SOP.md`, `BDS_FORGE_ECOSYSTEM_INTEGRATION_PROTOCOL_v1.md`

---

## 1. Purpose

This protocol defines how documentation is structured, authored, built, maintained, and consumed across every application in the Forge ecosystem. Documentation is a **first-class engineering deliverable** — not an afterthought, not a nice-to-have. Every line of production code must have a corresponding line of documentation that describes its intent, contract, and constraints.

This protocol exists because the Forge ecosystem uses AI-assisted development (Claude Code via VS Code) as its primary engineering workflow. Documentation is the **primary interface between the human architect and the AI executor**. Poor documentation produces poor code. Complete documentation produces governed, predictable, architecturally sound output.

---

## 2. The Documentation Stack

Every Forge application maintains a layered documentation stack. Each layer serves a distinct purpose and audience.

### 2.1 Required Documents

| Document | Purpose | Location | Format |
|----------|---------|----------|--------|
| `SYSTEM.md` | Complete system reference — architecture, schemas, APIs, patterns, integration points | Project root (build artifact) | Modular parts assembled via `BUILD.sh` |
| `CLAUDE.md` | Project-specific Claude instructions — module map, coding standards, context loading | Project root | Single Markdown file |
| Architecture Spec | Full design document — modules, data model, AI integration, UX, roadmap | `docs/` directory | Markdown (`.md`) |
| Extended Roadmap | Phase-by-phase implementation plan with dependencies, risks, success metrics | `docs/` directory | Markdown |
| Module Specs | Dedicated spec files for complex modules with their own data models and UX | `docs/` or project knowledge | Markdown |
| Integration Plan | Which ecosystem services this app uses, how, and why | Embedded in SYSTEM.md or standalone | Markdown |

### 2.2 Conditional Documents

These are required when the relevant subsystem is active:

| Document | Trigger | Purpose |
|----------|---------|---------|
| API Reference | App exposes HTTP endpoints | Complete endpoint docs organized by service |
| Database Schema | App owns or reads database tables | All tables, indexes, triggers, migration patterns |
| BugCheck Schemas | QA automation active | JSON Schema definitions for test artifacts |
| Module Specs | Module has its own data model, routes, or complex UX | Self-contained design spec per module |
| Prompting Plans | Multi-session implementation work | Session-by-session Claude Code prompts with acceptance criteria |

---

## 3. SYSTEM.md — The Canonical Reference

`SYSTEM.md` is the single source of truth for an application's technical reality. It answers: *"What does this system actually do, right now, and how?"*

### 3.1 What SYSTEM.md Is

- The **canonical technical reference** for the entire application
- A **build artifact** — never edited directly at the root
- The **primary context source** for AI-assisted development sessions
- A **living document** that reflects implemented reality, not aspirational design

### 3.2 What SYSTEM.md Is Not

- Not a tutorial or getting-started guide
- Not a marketing document or product brief
- Not a historical record of abandoned designs (those belong in Architecture Spec with supersession notices)
- Not a to-do list (roadmap items belong in the Extended Roadmap)

### 3.3 Required Sections

Every SYSTEM.md must contain these sections. Numbering is stable — new sections append, existing numbers never change.

| § | Section | Contents |
|---|---------|----------|
| 1 | Overview & Philosophy | What the app does, core principles (5-7 max), brand identity |
| 2 | Architecture | High-level diagram (text-based), service boundaries, data flow |
| 3 | Tech Stack | Every dependency with version, organized by layer (frontend, API, backend, infra) |
| 4 | Project Structure | Directory tree (2 levels deep), file naming conventions |
| 5 | Configuration & Environment | All env vars with types, defaults, ownership (which service reads them) |
| 6 | Design System | Colors, typography, spacing tokens, component patterns |
| 7 | Frontend | Framework specifics, routing, stores, component patterns |
| 8 | API Layer | Proxy patterns, middleware, auth, error contracts |
| 9 | Backend | Service logic, ORM patterns, async patterns |
| 10 | Ecosystem Integration | Which shared services (DataForge, NeuroForge, Rake, etc.) and how |
| 11 | Database Schema | Every table with columns, types, constraints, indexes, relationships |
| 12 | AI Integration | Prompt templates, routing, transparency, offline fallback |
| 13+ | Domain Sections | Module-specific sections (Export Pipeline, Series Management, Collaboration, etc.) |
| N-2 | Error Handling Contract | Error shapes, codes, UI patterns, retry policies |
| N-1 | Testing Infrastructure | Test tiers, coverage targets, preflight checks |
| N | Handover / Migration Notes | Stack reconciliation, superseded patterns, historical context |

### 3.4 Section Authoring Rules

Each section must follow these conventions:

**Voice:** Present tense, declarative. Describe what the system *does*, not what it *will* or *should* do. Future work belongs in the roadmap.

**Tables over prose:** Use tables for structured data (schemas, endpoints, env vars, dependencies). Tables are parseable by AI and scannable by humans.

**Code blocks:** Include actual code samples — TypeScript interfaces, SQL DDL, API request/response shapes, Svelte component signatures. These serve as executable contracts.

**No orphan references:** Every entity mentioned (table, endpoint, component, env var) must be defined somewhere in SYSTEM.md. If you reference `lore_entities`, the table definition must exist in §11.

**Version header:** Every SYSTEM.md begins with a version line and date:
```
**Document version:** 1.9 (2026-02-18) — Brief changelog note
```

---

## 4. Modular Documentation Architecture

Large reference documents (SYSTEM.md is the canonical case) must be split into numbered part files for maintainability, targeted editing, and selective context loading.

### 4.1 Directory Structure

```
doc/system/
├── _index.md                  # Master TOC + document version
├── 01-overview-philosophy.md
├── 02-architecture.md
├── 03-tech-stack.md
├── 04-project-structure.md
├── 05-configuration.md
├── 06-design-system.md
├── 07-frontend.md
├── 08-api-layer.md
├── 09-backend.md
├── 10-ecosystem-integration.md
├── 11-database-schema.md
├── 12-ai-integration.md
├── 13-export-pipeline.md       # Domain sections start here
├── ...
├── NN-error-handling.md
├── NN-testing.md
├── NN-handover.md
└── BUILD.sh                   # Concatenates parts → SYSTEM.md
```

### 4.2 Immutable Rules

1. **`SYSTEM.md` at project root is a build artifact** — never edit it directly. All edits happen in `doc/system/` part files.
2. **Numbering is stable** — once a section gets a number, that number never changes. New sections get the next available number. Renumbering is forbidden.
3. **Zero content loss** — every line of `SYSTEM.md` must exist in exactly one part file. The build script concatenates, it does not transform.
4. **One section per file** — no cramming multiple top-level sections into a single part file. Sub-sections within a section are fine.
5. **File names are descriptive** — the number prefix establishes order; the slug describes content. `11-database-schema.md` not `11-section.md`.

### 4.3 BUILD.sh Specification

The build script must:

```bash
#!/bin/bash
# BUILD.sh — Assembles SYSTEM.md from modular parts
set -euo pipefail

OUTPUT="../SYSTEM.md"
PARTS_DIR="$(dirname "$0")"

echo "Assembling SYSTEM.md..."

# Start with _index.md (TOC + version)
cat "$PARTS_DIR/_index.md" > "$OUTPUT"

# Concatenate all numbered parts in order
for part in "$PARTS_DIR"/[0-9][0-9]-*.md; do
  echo "" >> "$OUTPUT"
  echo "---" >> "$OUTPUT"
  echo "" >> "$OUTPUT"
  cat "$part" >> "$OUTPUT"
done

LINE_COUNT=$(wc -l < "$OUTPUT")
echo "✓ SYSTEM.md assembled: $LINE_COUNT lines"
```

**Requirements:**
- Must be idempotent (safe to run repeatedly)
- Must fail loudly if part files are missing or malformed (`set -euo pipefail`)
- Must report line count for sanity checking
- Must produce identical output given identical input (no timestamps injected)

---

## 5. Context Bundle System

The context bundle is how documentation enters Claude Code sessions. It exists to solve a specific problem: SYSTEM.md is too large for a single context window, but targeted work only needs a subset of sections.

### 5.1 Required Script

Every project must include `scripts/context-bundle.sh` with these capabilities:

| Flag | Behavior |
|------|----------|
| *(no args)* | Assembles core sections (~60K tokens, manageable context) |
| `--list` | Shows all available sections and presets |
| `--dry-run` | Preview with line counts before assembling |
| `--preset <name>` | Predefined section groups for common tasks |
| `--all` | Full assembly for comprehensive sessions |
| `07 11 17` | Cherry-pick specific sections by number |
| `--with-roadmap` | Append Extended Roadmap |
| `--with-specs` | Append all module specs |

### 5.2 Preset Design Principle

Group sections by **domain of work**, not alphabetically. A developer working on collaboration needs §7 (Frontend), §11 (DB Schema), §17 (Y.js Collab), §19 (Handover), §20 (Snapshot) — not §1–§5.

**Preset naming convention:** lowercase, hyphenated, descriptive of the work domain.

```bash
# Example presets
collab)       sections="07 11 17 19 20" ;;
frontend)     sections="06 07 08 16"    ;;
export)       sections="07 09 13 16"    ;;
ai)           sections="08 09 12 27"    ;;
testing)      sections="07 08 09 26"    ;;
full-stack)   sections="07 08 09 11 16" ;;
```

### 5.3 .gitignore Requirement

`context-bundle.md` is a generated artifact and must be listed in `.gitignore`. It never enters version control.

---

## 6. CLAUDE.md — The AI Instructions File

`CLAUDE.md` sits at the project root and provides Claude Code with project-specific behavioral instructions. It is distinct from SYSTEM.md in that it describes *how Claude should work on this project*, not *what the project is*.

### 6.1 Required Contents

| Section | Purpose |
|---------|---------|
| Module Map | List of all modules with routes, primary components, and data stores |
| Coding Standards | Language versions, framework idioms, style rules, forbidden patterns |
| File Conventions | Naming patterns, directory organization, where new files go |
| Context Loading | How to use `context-bundle.sh`, which presets exist, when to load what |
| Ecosystem Rules | Which services this app talks to, what's forbidden (direct API calls, etc.) |
| Testing Expectations | Test framework, assertion patterns, coverage requirements |
| Change Protocol | Patch vs. rewrite rules, what requires approval, what's autonomous |

### 6.2 Authoring Rules

- Keep it concise — CLAUDE.md is loaded at the start of every session. Bloat wastes context.
- Use imperative voice: "Use Svelte 5 runes. Never use legacy stores."
- Include negative rules: what Claude must *not* do is as important as what it should do.
- Update it when patterns change — stale CLAUDE.md produces inconsistent code.

---

## 7. Document Lifecycle

### 7.1 Creation Sequence

When starting a new Forge application, documents are created in this order:

```
1. CLAUDE.md              ← First. Establishes coding standards before any code.
2. Architecture Spec      ← Second. Full design document with module map and data model.
3. doc/system/ parts      ← Third. Build out SYSTEM.md part files from architecture spec.
4. BUILD.sh               ← Fourth. Assemble SYSTEM.md.
5. context-bundle.sh      ← Fifth. Create presets for development domains.
6. Extended Roadmap       ← Sixth. Phase-by-phase implementation plan.
7. Module Specs           ← As needed. Complex modules get their own specs.
8. Prompting Plans        ← As needed. Multi-session work gets structured prompts.
```

No production code is written before steps 1–4 are complete. This is a gate, not a suggestion.

### 7.2 Maintenance Cadence

| Trigger | Action |
|---------|--------|
| New feature implemented | Update relevant SYSTEM.md section(s) + rebuild |
| New module added | Create part file with next available number + update _index.md TOC |
| API endpoint added/changed | Update API Reference section |
| Database migration applied | Update Database Schema section |
| Dependency added/upgraded | Update Tech Stack section |
| Architecture decision made | Record in Architecture Spec; update SYSTEM.md if it affects current state |
| Design abandoned | Move to Architecture Spec with `[SUPERSEDED]` notice; remove from SYSTEM.md |
| Major milestone completed | Bump SYSTEM.md version number and changelog note |

### 7.3 The Documentation Debt Rule

Documentation debt follows the same priority as technical debt. If a section of SYSTEM.md is out of date:

1. **P0** — Schema or API section contradicts reality (causes incorrect code generation)
2. **P1** — Missing section for an implemented feature (causes Claude to guess)
3. **P2** — Section is accurate but incomplete (causes suboptimal code)
4. **P3** — Section exists but could be clearer (minor friction)

P0 documentation debt blocks all feature work until resolved.

---

## 8. Cross-Document Relationships

### 8.1 Authority Hierarchy

When documents conflict, this is the resolution order:

```
1. SYSTEM.md              ← Ground truth for what IS implemented
2. CLAUDE.md              ← Ground truth for how to WORK on it
3. Module Specs           ← Ground truth for module-specific design
4. Architecture Spec      ← Design intent (may diverge from reality)
5. Extended Roadmap       ← Future plans (explicitly not yet real)
6. Prompting Plans        ← Session-level tactical guidance
```

If the Architecture Spec says one thing and SYSTEM.md says another, SYSTEM.md wins — it describes reality. The Architecture Spec should be updated to reconcile, with a supersession notice for the old design.

### 8.2 Cross-Reference Convention

When one document references another, use this format:

```markdown
*See SYSTEM.md §11 for the complete schema.*
*See CARTOGRAPHERS_FORGE_SPEC.md §5 for travel time calculations.*
*Per BDS_VSCODE_CLAUDE_SOP.md §4, patches are preferred over full rewrites.*
```

Always reference by section number, never by heading text (headings can be edited; numbers are stable).

---

## 9. Quality Gates

### 9.1 New Application Gate

Before writing production code for a new Forge application, verify:

- [ ] `CLAUDE.md` exists with module map and coding standards
- [ ] `SYSTEM.md` exists (assembled from `doc/system/` parts via `BUILD.sh`)
- [ ] `_index.md` has complete TOC matching part file count
- [ ] `scripts/context-bundle.sh` exists with `--list`, `--dry-run`, and at least 3 presets
- [ ] `context-bundle.md` is in `.gitignore`
- [ ] Architecture spec exists with module map, data model, and integration plan
- [ ] Extended roadmap exists with phase dependencies
- [ ] All database tables documented with column types, constraints, and notes
- [ ] All API endpoints documented by service with request/response shapes
- [ ] All environment variables documented with types, defaults, and ownership
- [ ] Ecosystem integration section documents which shared services are used and why

### 9.2 Pull Request Gate

Before merging code that touches architecture, schemas, or APIs:

- [ ] Relevant SYSTEM.md section(s) updated in part files
- [ ] `BUILD.sh` run to regenerate SYSTEM.md
- [ ] No orphan references (new entities are defined, removed entities are dereferenced)
- [ ] Version number bumped if this is a significant change
- [ ] CLAUDE.md updated if coding patterns or module map changed

### 9.3 Session Start Gate

Before beginning a Claude Code development session:

- [ ] Appropriate context-bundle preset loaded (or manual section selection)
- [ ] SYSTEM.md version matches latest build
- [ ] CLAUDE.md loaded as foundational context
- [ ] Relevant module specs loaded if working on a specific module
- [ ] BDS_VSCODE_CLAUDE_SOP.md loaded (always)

---

## 10. Anti-Patterns

These are explicitly forbidden across the Forge ecosystem:

| Anti-Pattern | Why It's Forbidden |
|--------------|--------------------|
| Editing `SYSTEM.md` directly | Build artifact. Edits will be overwritten by next `BUILD.sh` run. |
| Renumbering existing sections | Breaks all cross-references and context-bundle presets. |
| Aspirational content in SYSTEM.md | SYSTEM.md describes *what is*, not *what will be*. Future work goes in the roadmap. |
| Documentation-free modules | Every module with its own route, data model, or API must be documented. No exceptions. |
| Stale schema sections | P0 debt. Incorrect schema docs cause Claude to generate wrong migrations and queries. |
| Context-bundle in git | Generated artifact. Clutters history and confuses CI. |
| Monolithic SYSTEM.md editing | Even for "quick fixes," edit the part file and rebuild. No shortcuts. |
| Copy-paste between docs | Each fact lives in one authoritative location. Other docs reference it, never duplicate it. |
| Undocumented env vars | Every env var must appear in §5 with type, default, and which service reads it. |
| Heading-based cross-references | Use `§N` section numbers. Headings change; numbers don't. |

---

## 11. Templates

### 11.1 _index.md Template

```markdown
# {Application Name} — Complete System Reference

> {One-line description capturing the product's essence.}
> "{Tagline}"

**Document version:** 1.0 ({date}) — Initial release

---

## Table of Contents

1. [Overview & Philosophy](#1-overview--philosophy)
2. [Architecture](#2-architecture)
3. [Tech Stack](#3-tech-stack)
4. [Project Structure](#4-project-structure)
5. [Configuration & Environment](#5-configuration--environment)
6. [Design System](#6-design-system)
7. [Frontend](#7-frontend)
8. [API Layer](#8-api-layer)
9. [Backend](#9-backend)
10. [Ecosystem Integration](#10-ecosystem-integration)
11. [Database Schema](#11-database-schema)
12. [AI Integration](#12-ai-integration)
{Additional domain sections as needed}
N-2. [Error Handling Contract](#error-handling-contract)
N-1. [Testing Infrastructure](#testing-infrastructure)
N. [Handover / Migration Notes](#handover--migration-notes)
```

### 11.2 Part File Template

```markdown
## {N}. {Section Title}

{Brief introductory paragraph — what this section covers and why.}

### {N}.1 {First Subsection}

{Content}

### {N}.2 {Second Subsection}

{Content}
```

### 11.3 CLAUDE.md Template

```markdown
# {Application Name} — Claude Instructions

## Module Map

| Module | Route | Primary Components | Data Store |
|--------|-------|-------------------|------------|
| {name} | {route} | {components} | {store/table} |

## Coding Standards

- {Language}: {version} with {specific idioms}
- {Framework}: {patterns to use, patterns to avoid}
- {Style}: {formatting, naming, file organization rules}

## Context Loading

```bash
# Default (core sections)
./scripts/context-bundle.sh

# Domain presets
./scripts/context-bundle.sh --preset {preset-name}

# Cherry-pick
./scripts/context-bundle.sh {section-numbers}
```

## Ecosystem Rules

- All data through DataForge — no direct database access
- All AI through NeuroForge — no direct provider calls
- All secrets through Forge_Command — no env var secrets in application code
- Fastify proxy for all external service communication

## Change Protocol

- Patches preferred over full rewrites
- New files require explicit approval
- Schema changes require migration documentation
- Follow Read → Think → Write
```

---

## 12. Versioning

### 12.1 SYSTEM.md Versioning

Version numbers follow `MAJOR.MINOR` format:

- **MAJOR** increments when: architecture changes, stack migrations, breaking schema changes
- **MINOR** increments when: new sections added, existing sections significantly updated, new integrations documented

Version bumps happen at the point of documentation update, not at the point of code change. If you implement a feature on Monday and document it on Wednesday, the version bumps on Wednesday.

### 12.2 Protocol Versioning

This protocol itself follows the same `MAJOR.MINOR` pattern. Breaking changes to the protocol (new required documents, new mandatory sections) increment MAJOR. Clarifications and additions increment MINOR.

---

## 13. Adoption Checklist

For existing Forge applications that predate this protocol, achieve compliance by completing:

- [ ] Verify `doc/system/` modular structure exists (migrate from monolithic SYSTEM.md if needed)
- [ ] Verify `BUILD.sh` produces identical output to current SYSTEM.md
- [ ] Verify `_index.md` TOC matches all part files
- [ ] Verify all mandatory sections (§1–§12) exist, even if sparse
- [ ] Verify `CLAUDE.md` exists and is current
- [ ] Verify `scripts/context-bundle.sh` exists with at least 3 presets
- [ ] Verify `context-bundle.md` is in `.gitignore`
- [ ] Verify no aspirational content in SYSTEM.md (migrate to roadmap)
- [ ] Verify all cross-references use `§N` notation
- [ ] Run `BUILD.sh` and diff against current SYSTEM.md — zero drift tolerance

---

*This protocol is itself a living document. Propose changes through the standard spec review process.*
