---
name: architecture-mapper
description: Scaffold a stack-aware reverse-engineering workflow into a legacy or unfamiliar codebase. Detects the project's tech stack (Node/Express/Mongo + Vue/React, Python with Django/Flask/FastAPI, or generic) and writes a tailored CLAUDE.md, a set of `.claude/commands/*.md` slash commands, and a `docs/architecture/` seed into the target repo so the user can then run `/architecture-bootstrap`, `/module-map`, `/steel-threads`, `/workflows`, `/data-flow`, and more. Use this whenever the user asks to map, reverse-engineer, audit, document, or understand the architecture of an existing codebase; wants module maps, steel threads, request lifecycles, data-flow diagrams, or workflow documentation; is onboarding to a legacy or unfamiliar repo; or says things like "how does this codebase work", "help me understand this repo", "generate an architecture report", or "create a code map". Trigger even when the user doesn't use the word "architecture" explicitly but describes exploring, auditing, or documenting how an existing system works end-to-end.
---

# Architecture Mapper

This skill installs a reverse-engineering workflow into a target repo — built for large, confusing legacy codebases that have lost solid requirements and need a comprehensive drillable map. After it runs, the user has:

- a `CLAUDE.md` that teaches Claude Code how to analyze *their* stack and how to produce cross-linked outputs,
- 17 stack-tailored slash commands under `.claude/commands/`, including the orchestrator `/architecture-run-all` that runs the full pipeline end-to-end,
- a seeded `docs/architecture/` folder where analysis outputs accumulate — every output is cross-linked so the user can click through from a steel thread into a module into an entity without leaving the knowledge base.

After install, the user can either run `/architecture-run-all` (one command, full pipeline) or step through the individual commands manually. Both produce the same artifacts.

## Invocation

There are three ways to trigger this skill. **All of them run the same install/scaffold flow in the Process section below** — they differ only in how much the user has pre-committed.

- **`/architecture-mapper install`** — the explicit entrypoint. Type it from inside the repo you want to map. `$ARGUMENTS` will be `install` (plus any extra tokens). This means *the user has already opted into scaffolding* — do not ask "do you want to install a 17-command workflow?"; go straight to detection and a single confirm-then-write. Optional extra tokens in `$ARGUMENTS`:
  - a **path** → use it as the target repo instead of the current working directory (e.g. `/architecture-mapper install ../legacy-app`).
  - **`--stack <node-express-mongo|python-web|generic>`** → skip auto-detection and use that profile directly.
  - **`--force`** → resolve any collisions by backing up (`<file>.bak-<date>`) and overwriting without pausing to ask. Never destroys without a backup.
- **`/architecture-mapper`** (no argument) — same flow, auto-detecting the stack, with the normal Step 1 consent confirm.
- **Natural language** — "map this repo", "how does this codebase work end-to-end", etc. Auto-triggers the same flow.

At the start of Step 1, read `$ARGUMENTS`. If the first token is `install`, set "explicit-install mode": parse any path / `--stack` / `--force` tokens, honour them, and collapse Steps 1 and 3 into one combined "here's the target + detected stack, writing now" confirmation before the write. Otherwise run Steps 1–6 normally.

> The colon form `/architecture-mapper:install` does **not** work — `:`-namespaced sub-commands are a plugin-only feature, and this ships as a personal/project skill. Use the space form: `/architecture-mapper install`.

## Why it's built this way

The underlying workflow (from `code-map-architecture.md`) is genuinely good but hardcodes a Vue+Express+Mongo stack. Trying to run it on an ASP.NET app or a Django service produces generic, stack-mismatched hunt lists that miss the real entry points. Two fixes combine in this skill:

1. Split the workflow into a stack-neutral scaffold plus stack-specific "hunt hints" swapped in at install time.
2. Make every output a node in a cross-linked knowledge base (anchor slugs + clickable Mermaid diagrams + backlinks) instead of 13 disconnected markdown files. The composite `/architecture-flowchart` and `/architecture-index` passes turn the individual artifacts into a drillable map.

## Process

### Step 1 — Confirm the target directory

First, read `$ARGUMENTS` (see **Invocation**). If its first token is `install`, you're in **explicit-install mode**: the user has opted in, so don't re-ask whether to install — extract any path / `--stack` / `--force` tokens and carry them forward. Otherwise proceed normally.

Identify the target repo. By default it's the current working directory. If `$ARGUMENTS` (or the user's message) references a different path, use that. Before doing anything, confirm:

> "I'll install the architecture-mapping workflow into `<path>`. This will create `CLAUDE.md`, `.claude/commands/`, and `docs/architecture/` — ok to proceed?"

In explicit-install mode you may skip this standalone confirm and instead fold the target + detected stack into the single Step 3 summary shown right before writing.

Do not touch the skill's own folder or anything under `~/.claude/`. The install target is always a user project directory.

### Step 2 — Detect the stack

If `$ARGUMENTS` contains `--stack <name>`, skip detection entirely and use that profile (`references/stacks/<name>.md`); record one evidence line noting the stack was user-forced, then go to Step 3. Otherwise:

Read `references/detection.md`. Walk its precedence table against the target repo using Glob + Read. Stop at the first confident match. Record the evidence (which files + which deps) — you'll show it to the user.

Possible outcomes:

- **Single stack match** → proceed to Step 3 with that stack's reference file.
- **Multiple stack matches** (e.g., a repo with both `package.json` and `requirements.txt`) → show evidence for each and ask the user which is primary. Only scaffold one stack per install.
- **No match** → use `references/stacks/generic.md`. Tell the user the fallback is active and which sections will be thinner as a result.

### Step 3 — Show detection + confirm

Present a short summary:

```
Detected stack: <name>
Evidence:
  - <file>: <finding>
  - <file>: <finding>
Profile: references/stacks/<file>.md
```

Ask the user to confirm or override. If they override (e.g., "use the Python profile even though you found package.json"), honour it — this is their judgment call.

### Step 4 — Check for collisions

Before any write, check whether the target repo already contains:

- `CLAUDE.md`
- `.claude/commands/` with files already in it
- `docs/architecture/`

If any exist, show the user what's there and offer:

- **Back up + install** — rename existing to `<name>.bak-<date>` then write fresh.
- **Merge** — append the skill's content into the existing file, clearly fenced with a heading like `## Architecture Mapper (installed <date>)`.
- **Skip that file** — leave it alone, install the rest.

Never silently overwrite. A pre-existing `CLAUDE.md` likely contains the user's own project memory and is load-bearing for their daily workflow.

In explicit-install mode with `--force`, don't prompt: apply **Back up + install** to every collision automatically, then report which files were renamed to `<name>.bak-<date>`. `--force` still never deletes without a backup.

### Step 5 — Install

Follow `references/install-procedure.md`. In short: read each file from `assets/`, substitute placeholders using values from the chosen stack reference, write to the target repo. Use the Write tool (new files) and Edit (merges).

Placeholders to substitute: `{{STACK_NAME}}`, `{{STACK_SUMMARY}}`, `{{ENTRY_POINT_HINTS}}`, `{{ROUTE_LAYER_HINTS}}`, `{{DATA_ACCESS_HINTS}}`, `{{BACKGROUND_WORK_HINTS}}`, `{{INTEGRATION_HINTS}}`, `{{FRONTEND_HINTS}}`, `{{UI_SURFACE_HINTS}}`, `{{HUNT_PRIORITY_LIST}}`, `{{MONGODB_NOTE}}`, `{{RELATIONAL_NOTE}}`. The stack reference file lists exactly what each one should contain for that stack.

After every file is written, verify by re-reading at least `CLAUDE.md`, `.claude/commands/module-map.md`, and `.claude/commands/ui-surface-map.md` and confirming no `{{...}}` tokens remain.

### Step 6 — Hand off

Tell the user the install is complete and offer them the two paths. Use this template:

> Installed. Two ways to run:
>
> **Recommended — one shot.** Run `/architecture-run-all` and come back to a finished drillable report. Add `--checkpoint` if you want to inspect intermediate milestones. This is the right choice for large, unfamiliar codebases where you want the full picture assembled.
>
> **Manual — one step at a time.** Run these in order; each builds on the previous outputs in `docs/architecture/`. Useful when you want to inspect each pass as it runs, or when you only need a subset.
>
> 1. `/architecture-bootstrap` — breadth-first inventory
> 2. `/repo-inventory` — subsystem grouping
> 3. `/module-map` — module boundaries + dependency graph
> 4. `/entry-trace` — entry points into the system
> 5. `/ui-surface-map` — widget → endpoint → data (skip for headless stacks)
> 6. `/request-lifecycle` — backend request flow
> 7. `/data-model-map` — entities, persistence, access patterns
> 8. `/background-jobs` — async/scheduled work
> 9. `/integrations-map` — external boundaries
> 10. `/steel-threads` — top end-to-end flows
> 11. `/workflows` — business/operational flows
> 12. `/data-flow` — system-wide data movement
> 13. `/architecture-flowchart` — composite clickable diagram
> 14. `/architecture-critic` — self-review + revise
> 15. `/architecture-index` — generate the INDEX.md hub
> 16. `/architecture-report` — consolidated final doc
>
> The drillable output lives in `docs/architecture/INDEX.md` once the pipeline completes. Open it in VSCode (or any Mermaid-aware renderer) and click through.

You may offer to run `/architecture-run-all` on behalf of the user if they say yes, but don't start it unprompted — the skill's job is scaffolding; running the pipeline is a second, separate act.

## What's in this skill

```
architecture-mapper/
├── SKILL.md                    ← you are here
├── references/
│   ├── detection.md            ← stack-marker precedence table
│   ├── install-procedure.md    ← substitute-and-write sequence + collision handling
│   ├── command-catalog.md      ← one-line purpose of each of the 17 commands
│   └── stacks/
│       ├── node-express-mongo.md
│       ├── python-web.md
│       └── generic.md
└── assets/
    ├── CLAUDE.md.tmpl
    ├── commands/               ← 17 slash-command templates
    │   ├── architecture-run-all.md       ← orchestrator
    │   ├── architecture-bootstrap.md
    │   ├── repo-inventory.md
    │   ├── module-map.md
    │   ├── entry-trace.md
    │   ├── ui-surface-map.md             ← widget → endpoint → data
    │   ├── request-lifecycle.md
    │   ├── data-model-map.md
    │   ├── background-jobs.md
    │   ├── integrations-map.md
    │   ├── steel-threads.md
    │   ├── workflows.md
    │   ├── data-flow.md
    │   ├── architecture-flowchart.md     ← composite clickable diagram
    │   ├── architecture-critic.md
    │   ├── architecture-index.md         ← hub generator
    │   └── architecture-report.md
    └── docs-seeds/             ← INDEX.md + progress.md + unknowns.md
```

Read the referenced files on demand — no need to load them all upfront.

## Adding a new stack later

Drop a new `references/stacks/<name>.md` that defines all placeholders, add a detection rule to `references/detection.md`, done. No code changes.

## When this skill is the wrong tool

- The user wants a **live** architecture query answered right now ("how does login work in this repo?") — just answer directly using Explore/Grep/Read. Don't install a 13-command workflow for a one-off question.
- The user wants to **change** architecture (refactor, extract a module) — use `improve-codebase-architecture` instead.
- The user wants to **document a design they're about to build** — that's a PRD job, not a reverse-engineering job.
