# architecture-mapper

A Claude Code **agent skill** that installs a stack-aware reverse-engineering workflow into a legacy or unfamiliar codebase.

After install, the target repo has:

- a tailored `CLAUDE.md` that teaches Claude Code how to analyze *its* stack
- 17 stack-tailored slash commands under `.claude/commands/`, including the orchestrator `/architecture-run-all`
- a seeded `docs/architecture/` folder where every analysis output is cross-linked into a drillable knowledge base

Supported stacks:

- **Node.js** + Express/Fastify/Koa/NestJS + Mongo/relational + Vue/React/Next
- **Python web** — Django / Flask / FastAPI + Celery/RQ + SQLAlchemy/Django ORM
- **Generic fallback** for everything else (Go, Rust, Java, .NET, Ruby, PHP, Elixir, …)

## Install

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

## Use

Once installed, just ask Claude Code to map, reverse-engineer, audit, or document the architecture of a codebase. The skill auto-triggers on prompts like:

- "help me understand this repo"
- "generate an architecture report"
- "create a code map"
- "how does this codebase work end-to-end"

The skill will detect the stack, show you the evidence, confirm the target directory, handle any collisions with existing `CLAUDE.md` / `.claude/commands/` / `docs/architecture/`, then install.

After install, two run modes are available inside the target repo:

- **`/architecture-run-all`** — one command, full pipeline, autonomous. Add `--checkpoint` to pause at 4 milestones.
- **Manual** — step through `/architecture-bootstrap`, `/module-map`, `/steel-threads`, `/workflows`, `/data-flow`, etc. in order.

Both produce the same cross-linked artifacts under `docs/architecture/`, entered from `docs/architecture/INDEX.md`.

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
