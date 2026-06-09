# architecture-mapper

A Claude Code **agent skill** that installs a stack-aware reverse-engineering workflow into a legacy or unfamiliar codebase.

> **There are two distinct steps, and they are not the same thing.**
> 1. **Install the skill** (clone it into your skills folder). This makes the skill *available* as the command `/architecture-mapper`. It does **not** create the analysis commands.
> 2. **Run the skill** against a repo — `/architecture-mapper install` (or just ask in plain language). The skill then **scaffolds** the 17 analysis commands into that repo's `.claude/commands/`.
>
> `/architecture-run-all` and the other 16 commands **do not exist until step 2 runs against a target repo.** If you just installed the skill and typed `/architecture-run-all`, Claude won't recognize it — see [Troubleshooting](#troubleshooting--architecture-run-all-not-recognized).

After the skill has been **run against a target repo**, that repo has:

- a tailored `CLAUDE.md` that teaches Claude Code how to analyze *its* stack
- 17 stack-tailored slash commands under `<repo>/.claude/commands/`, including the orchestrator `/architecture-run-all`
- a seeded `docs/architecture/` folder where every analysis output is cross-linked into a drillable knowledge base

Supported stacks:

- **Node.js** + Express/Fastify/Koa/NestJS + Mongo/relational + Vue/React/Next
- **Python web** — Django / Flask / FastAPI + Celery/RQ + SQLAlchemy/Django ORM
- **Generic fallback** for everything else (Go, Rust, Java, .NET, Ruby, PHP, Elixir, …)

## Install (step 1 — makes the skill available)

This is a Claude Code skill. Copy the skill directory into your Claude Code skills folder and restart Claude Code:

- **User-scoped (available in every project):** `~/.claude/skills/architecture-mapper/`
- **Project-scoped (only in this repo):** `<repo>/.claude/skills/architecture-mapper/`

The directory must contain `SKILL.md` at its root — that file's frontmatter is what Claude Code reads to decide when to invoke the skill.

```bash
# user-scoped install (bash)
git clone <this-repo-url> ~/.claude/skills/architecture-mapper
```

```powershell
# user-scoped install (PowerShell)
git clone <this-repo-url> "$env:USERPROFILE\.claude\skills\architecture-mapper"
```

## Use (step 2 — scaffolds the slash commands into your repo)

Open Claude Code **inside the repo you want to analyze**, then trigger the skill one of two ways:

### Explicit command (recommended — clearest)

```
/architecture-mapper install
```

Once the skill is installed (step 1), Claude Code exposes it as the slash command `/architecture-mapper` (the command name comes from the skill's directory). Adding the `install` argument tells it you've already opted in, so it goes straight to: detect the stack → show you the target + evidence → write the files. Optional arguments:

```
/architecture-mapper install ../legacy-app          # target a different path than the cwd
/architecture-mapper install --stack python-web      # skip auto-detect, force a profile
/architecture-mapper install --force                 # back up & overwrite collisions without prompting
```

> Note: `/architecture-mapper:install` (colon) does **not** work — colon sub-commands are a Claude Code *plugin* feature, and this ships as a plain skill. Use the space form `/architecture-mapper install`. Bare `/architecture-mapper` works too; it just runs with the normal "ok to proceed?" confirm.

### Natural language (also works)

From inside the target repo, just ask Claude Code in plain language to map, reverse-engineer, audit, or document its architecture. The skill auto-triggers on prompts like:

- "help me understand this repo"
- "generate an architecture report"
- "create a code map"
- "how does this codebase work end-to-end"

### Either way

The skill detects the stack, shows you the evidence, confirms the target directory, handles any collisions with existing `CLAUDE.md` / `.claude/commands/` / `docs/architecture/`, then writes the files. **This write step is what creates the slash commands** in `<repo>/.claude/commands/`. Claude Code hot-loads them, so they're usable immediately in that repo — no restart needed.

Once scaffolded, two run modes are available **inside that target repo**:

- **`/architecture-run-all`** — one command, full pipeline, autonomous. Add `--checkpoint` to pause at 4 milestones.
- **Manual** — step through `/architecture-bootstrap`, `/module-map`, `/steel-threads`, `/workflows`, `/data-flow`, etc. in order.

Both produce the same cross-linked artifacts under `docs/architecture/`, entered from `docs/architecture/INDEX.md`.

## Troubleshooting — `/architecture-run-all` not recognized

This is the most common confusion, and it's expected behavior, not a bug:

- **The slash commands are per-repo, not global.** They live at `<your-repo>/.claude/commands/*.md`. Claude Code does **not** scan a skill's own `assets/commands/` folder, so cloning the skill to `~/.claude/skills/architecture-mapper/` creates **no** commands.
- **You must run the skill first.** Open the repo you want to map and run `/architecture-mapper install` (or ask Claude in words to "map this codebase's architecture"). Let it complete the install/scaffold step. *Then* `/architecture-run-all` exists. Note `/architecture-mapper` (the skill) and `/architecture-run-all` (a scaffolded pipeline command) are different things — the first creates the second.
- **Check it landed:** after scaffolding, you should see `<your-repo>/.claude/commands/architecture-run-all.md`. If that file isn't there, the scaffold step didn't run or targeted a different directory.
- **You must be in the scaffolded repo.** The command only resolves when your Claude Code session's working directory is the repo whose `.claude/commands/` holds it (or you've added it via `--add-dir`).

If `<your-repo>/.claude/commands/architecture-run-all.md` exists and you're in that repo but the command still doesn't resolve, start a new session in that directory so the commands are picked up.

## What's in the repo

```
architecture-mapper/
├── SKILL.md                      ← skill frontmatter + install flow
├── references/
│   ├── detection.md              ← stack-marker precedence table
│   ├── install-procedure.md      ← substitute-and-write sequence + collision handling
│   ├── command-catalog.md        ← one-line purpose of each of the 17 commands
│   └── stacks/
│       ├── node-express-mongo.md
│       ├── python-web.md
│       └── generic.md
├── assets/
│   ├── CLAUDE.md.tmpl            ← tailored project memory for the target repo
│   ├── commands/                 ← 17 slash-command templates
│   └── docs-seeds/               ← INDEX.md + progress.md + unknowns.md seeds
└── scripts/
    └── install_simulator.py      ← dry-run the install into a tmp dir, for testing
```

## Testing the install locally

The skill itself is meant to be invoked by Claude Code, but you can dry-run the substitute-and-write pass with the included script:

```bash
python scripts/install_simulator.py . node-express-mongo /tmp/arch-test
# or
python scripts/install_simulator.py . python-web /tmp/arch-test
python scripts/install_simulator.py . generic /tmp/arch-test
```

The script parses the chosen stack file's `## {{TOKEN}}` fences, substitutes every placeholder in the templates, writes the output tree, and verifies no `{{...}}` tokens survived. Exit code 0 means a clean install.

## Adding a new stack

1. Drop a new `references/stacks/<name>.md` defining all placeholder values (`## {{TOKEN_NAME}}` headings + fenced blocks).
2. Add a detection rule to `references/detection.md` at the right precedence.

No code changes needed.

## When this skill is the wrong tool

- You want a **live** architecture answer right now ("how does login work in this repo?") — just ask Claude directly. Don't install a 17-command workflow for a one-off question.
- You want to **change** architecture (refactor, extract a module) — use a refactoring-focused skill instead.
- You want to **document a design you're about to build** — that's a PRD workflow, not a reverse-engineering one.

## License

MIT — see [LICENSE](./LICENSE).
