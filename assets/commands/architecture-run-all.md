Run the full architecture-mapping pipeline end-to-end for this {{STACK_NAME}} codebase.

Arguments: $ARGUMENTS

By default, this command runs **autonomously** — all passes execute in sequence with no user prompts between them. Pass `--checkpoint` to pause at 4 major milestones so you can inspect and course-correct.

## Mode detection

Inspect `$ARGUMENTS`:

- Contains `--checkpoint` → **checkpoint mode**. After each milestone, write a short milestone summary to the chat, then stop and wait for explicit user go-ahead ("continue", "proceed", "next") before resuming.
- Otherwise → **autonomous mode**. No pauses, no intermediate confirmations. Report only if something blocks progress (e.g., missing frontend folder makes `/ui-surface-map` a no-op — note it and proceed).

## Pipeline

Execute every step below in order. Between steps, verify the expected output file exists before moving on. If a step fails or produces an empty artifact, write the failure to `docs/architecture/progress.md` and continue — do not abort the whole pipeline for one weak pass.

Each step is performed by following the corresponding slash-command file in `.claude/commands/`. Read that file, then execute its instructions. You are running these as subtasks, not re-invoking the slash-command system.

### Milestone 1 — Inventory
1. `/architecture-bootstrap` → `repo-inventory.md`, `entry-points.md`, `progress.md`, `unknowns.md`
2. `/repo-inventory` → deepens `repo-inventory.md`
3. `/module-map` → `module-map.md`

**Checkpoint 1 (if `--checkpoint`):** summarize what modules and entry points were found; pause.

### Milestone 2 — Surface + request flow
4. `/entry-trace` → `entry-points.md` (deepened), plus `vue-to-api-map.md` or `frontend-to-api-map.md` if frontend present
5. `/ui-surface-map` → `ui-surface-map.md` (only if frontend; otherwise no-op with a note)
6. `/request-lifecycle` → `api-lifecycle.md`

### Milestone 3 — Data + async + integrations
7. `/data-model-map` → `data-models.md`
8. `/background-jobs` → `background-jobs.md`
9. `/integrations-map` → `integrations.md`

**Checkpoint 2 (if `--checkpoint`):** summarize the entity catalog and external boundaries; pause.

### Milestone 4 — Narratives
10. `/steel-threads` → `steel-threads.md`
11. `/workflows` → `workflows.md`
12. `/data-flow` → `data-flow.md`

**Checkpoint 3 (if `--checkpoint`):** summarize the top 3 steel threads and the system-wide data movement; pause.

### Milestone 5 — Compile + critic + report
13. `/architecture-flowchart` → `system-flowchart.md`
14. `/architecture-critic` → revises multiple files, updates `progress.md`
15. `/architecture-index` → `INDEX.md`
16. `/architecture-report` → `final-report.md`

**Checkpoint 4 (if `--checkpoint`):** present the final-report summary and the INDEX hub; stop.

## Resumption

If this command is re-run on a repo that already has `docs/architecture/` populated, do not start over. Read `progress.md` to see what's complete, then pick up from the first incomplete step. Commands are idempotent by design — re-running a completed step refreshes the doc rather than duplicating content.

## Rules

- Pass `$ARGUMENTS` (minus the mode flag) through to sub-commands when it looks like a topic filter (e.g., `--autonomous --focus=billing`).
- Follow the cross-linking conventions in `CLAUDE.md` on every artifact produced. Do not break the chain mid-pipeline — if you run out of context, summarize into `progress.md` and stop cleanly so the next run resumes.
- Budget context aggressively. Between steps, discard source-file detail you've already captured into the docs; re-derive from the docs, not from raw source.
- The `--checkpoint` pauses are not optional when the flag is set. Stop and wait, even if the previous step was clean.

## When to refuse autonomous mode

Autonomous mode is fine for almost every repo. Refuse and force `--checkpoint` only if:

- The target directory contains uncommitted changes that suggest an in-progress edit (don't drown real work in generated docs).
- `CLAUDE.md` is missing — the skill wasn't installed yet. Tell the user to run the architecture-mapper skill first.

Otherwise, proceed end-to-end and produce the full drillable knowledge base.
