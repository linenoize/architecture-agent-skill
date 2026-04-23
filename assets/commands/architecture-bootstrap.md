Create the initial architecture workspace for this {{STACK_NAME}} codebase.

Arguments: $ARGUMENTS

Tasks:
1. Read `CLAUDE.md`.
2. Create `docs/architecture/` if missing.
3. Inspect the top-level structure:
{{ENTRY_POINT_HINTS}}
4. Identify:
   - the likely runtime entry points (HTTP, CLI, worker, scheduler)
   - how the app is wired together at boot
   - config/env files and where they're loaded
   - persistence setup
   - frontend bootstrap if applicable
   - background libraries in use
5. Write or update:
   - `docs/architecture/repo-inventory.md`
   - `docs/architecture/entry-points.md`
   - `docs/architecture/progress.md`
   - `docs/architecture/unknowns.md`

Required sections in the outputs:
- repository shape
- stack confirmation (does what you see match what CLAUDE.md says?)
- likely runtime surfaces
- top 10 investigation targets
- missing information / ambiguity

Rules:
- breadth-first only for this command — no deep tracing yet
- include file-path evidence for every claim
- label each finding **confirmed** / **likely** / **speculative**

## Required linking

Follow the cross-linking conventions in `CLAUDE.md`:
- Any runtime entry point you list in `entry-points.md` gets an anchor `### {name} {#endpoint-{method}-{path-slug}}` (HTTP), `#cli-{name}`, `#worker-{name}`, or `#scheduler-{name}` as appropriate.
- End each produced file with a `## Backlinks` section listing which other architecture docs are expected to reference it (at this stage, noting "to be populated by later passes" is fine).
