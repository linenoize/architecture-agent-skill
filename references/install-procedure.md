# Install procedure

This runs after detection and user confirmation (see SKILL.md steps 3-4). By this point you know the stack profile and have handled any collisions.

## What gets written

Into the target repo:

```
<target>/
├── CLAUDE.md
├── .claude/
│   └── commands/
│       ├── architecture-run-all.md         ← new: orchestrator
│       ├── architecture-bootstrap.md
│       ├── repo-inventory.md
│       ├── module-map.md
│       ├── entry-trace.md
│       ├── ui-surface-map.md               ← new: widget → endpoint → data
│       ├── request-lifecycle.md
│       ├── data-model-map.md
│       ├── background-jobs.md
│       ├── integrations-map.md
│       ├── steel-threads.md
│       ├── workflows.md
│       ├── data-flow.md
│       ├── architecture-flowchart.md       ← new: composite clickable diagram
│       ├── architecture-critic.md
│       ├── architecture-index.md           ← new: INDEX.md hub generator
│       └── architecture-report.md
└── docs/
    └── architecture/
        ├── INDEX.md                        ← new: hub seed
        ├── progress.md
        └── unknowns.md
```

17 command files, 1 CLAUDE.md, 3 docs seeds — 21 files total.

## Placeholder contract

Every template file in `assets/` may contain any of the tokens below. The stack reference file (`references/stacks/<stack>.md`) is the single source of truth for the substitution value of each token for the chosen stack.

| Token                       | What it's for                                                                                     | Example value (Node profile)                                                                    |
| --------------------------- | ------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| `{{STACK_NAME}}`            | Short human-readable stack name                                                                    | `Node.js + Express + MongoDB + Vue/React`                                                       |
| `{{STACK_SUMMARY}}`         | 2-3 sentence positioning line for the top of CLAUDE.md                                             | "An npm-managed JS/TS full-stack app using an Express-style backend, MongoDB for persistence..." |
| `{{ENTRY_POINT_HINTS}}`     | Bulleted files/patterns where the app starts                                                       | `server.js`, `app.js`, `src/server.js`, `bin/www`, Vue `main.js`                                |
| `{{ROUTE_LAYER_HINTS}}`     | How routes/endpoints are declared in this stack                                                    | `app.use(...)`, `router.get/post/...`, middleware chains                                        |
| `{{DATA_ACCESS_HINTS}}`     | ORM/driver/model patterns                                                                          | Mongoose schemas, `mongodb` driver usage, aggregate pipelines, `.populate()`                    |
| `{{BACKGROUND_WORK_HINTS}}` | Queues/schedulers/workers typical in this stack                                                    | `bullmq`, `agenda`, `node-cron`, `setInterval` as scheduler, worker processes                   |
| `{{INTEGRATION_HINTS}}`     | HTTP clients, SDKs, webhook conventions                                                            | `axios`/`fetch`/`got`, email SDKs, webhook route handlers                                       |
| `{{FRONTEND_HINTS}}`        | Frontend entry points — empty string for backend-only stacks                                       | Vue `createApp`, React `createRoot`, Pinia/Vuex/Redux stores, `<script setup>`                  |
| `{{UI_SURFACE_HINTS}}`      | How to inventory UI widgets (buttons/forms/tables/actions) — drives `/ui-surface-map`              | Vue template widgets, React JSX + handlers, Django templates + `{% url %}`, HTMX attributes     |
| `{{HUNT_PRIORITY_LIST}}`    | Numbered list used in CLAUDE.md "What to hunt first"                                               | See each stack file                                                                             |
| `{{MONGODB_NOTE}}`          | Data-model guidance for Mongo — empty if stack is relational                                       | "This is MongoDB — relationships are code-managed, not DB-enforced. Don't assume stored procs." |
| `{{RELATIONAL_NOTE}}`       | Data-model guidance for relational DBs — empty if stack is Mongo or none                           | "This is a relational DB. Look for migrations, stored procs, views, and FK constraints."        |

If a token is present in a template but the chosen stack reference doesn't define it, substitute an empty string and continue. Do not leave the literal token in the output.

## Step-by-step

1. **Load the stack reference.** Read `references/stacks/<chosen>.md`. Parse its "Placeholder values" section — each placeholder has a code-fenced block under a `## {{TOKEN_NAME}}` heading.

2. **Read each template.** Use Read on `assets/CLAUDE.md.tmpl`, `assets/commands/*.md` (in alphabetical order for determinism), and `assets/docs-seeds/*.md`.

3. **Substitute.** For each template, do a literal find-and-replace for every token. Use `replace_all: true` if going through Edit; if you pre-compose the final string and use Write, do the substitutions in memory and write once.

4. **Write to target.**
   - `assets/CLAUDE.md.tmpl` → `<target>/CLAUDE.md`
   - `assets/commands/<name>.md` → `<target>/.claude/commands/<name>.md`
   - `assets/docs-seeds/<name>.md` → `<target>/docs/architecture/<name>.md`

   Create the `.claude/commands/` and `docs/architecture/` directories if they don't exist (use Bash `mkdir -p` — forward slashes work on Windows too per the user's environment).

5. **Verify.** Read the written `CLAUDE.md` and `module-map.md`. Grep for `{{` in each. If any token survives, stop and report the bug — don't hand off a half-substituted install.

## Collision handling

For any pre-existing file at a target path:

- **Back up + install** (recommended default): Rename existing to `<filename>.bak-<YYYY-MM-DD>`. Write the new file fresh. Tell the user which files were backed up.
- **Merge** (CLAUDE.md only — commands and docs seeds shouldn't merge cleanly): Append the skill's content to the existing file under a fenced section:

  ```md
  ---

  ## Architecture Mapper (installed <YYYY-MM-DD>)

  <skill content>
  ```

  Do this with Edit so the user's existing content is preserved exactly.

- **Skip**: Don't write that one file. Keep going for the rest.

Ask once for the overall strategy; don't prompt per-file unless strategies genuinely differ.

## Partial install handling

If a write fails partway through, leave the target in a documented state: tell the user exactly which files were written and which weren't. Don't try to auto-rollback — the user may want to keep what got written so far. Let them decide.

## What not to do

- Install ends at Step 6 of SKILL.md — hand off to the user with the orchestrator offer. You may propose running `/architecture-run-all`, but don't start it without explicit consent.
- Don't modify `.gitignore`, `package.json`, or any build/config file in the target repo. This skill only adds the three paths listed above.
- Don't offer to commit the generated files. That's the user's call; they may want to review first.
