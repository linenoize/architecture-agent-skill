"""
Dry-run the architecture-mapper install into a target directory.

Mirrors what the skill itself would do when Claude invokes it:
- Parse the chosen stack file's ## {{TOKEN}} fenced blocks
- Read each template
- Apply literal find-and-replace for every token
- Write outputs to <target>/CLAUDE.md, <target>/.claude/commands/, <target>/docs/architecture/

Usage: python install_simulator.py <skill_dir> <stack_name> <target_dir>
"""
import re
import sys
from pathlib import Path


def parse_stack(stack_path: Path) -> dict[str, str]:
    """Extract each placeholder's value from the stack file.

    A placeholder is declared as `## {{TOKEN}}` followed by a fenced code block.
    We take the FIRST fence that appears under each heading as the value.
    """
    text = stack_path.read_text(encoding="utf-8")
    values: dict[str, str] = {}

    heading_re = re.compile(r"^##\s+\{\{([A-Z_]+)\}\}\s*$", re.MULTILINE)
    fence_re = re.compile(r"```[^\n]*\n(.*?)```", re.DOTALL)

    headings = list(heading_re.finditer(text))
    for i, m in enumerate(headings):
        token = m.group(1)
        start = m.end()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        block = text[start:end]
        fence = fence_re.search(block)
        values[token] = fence.group(1).rstrip("\n") if fence else ""

    return values


def substitute(template: str, values: dict[str, str]) -> str:
    """Apply literal find-and-replace for every {{TOKEN}} in the template.

    Tokens not present in values are left intact so verification can flag them.
    (The real install would substitute empty string + warn.)
    """
    out = template
    for token, value in values.items():
        out = out.replace(f"{{{{{token}}}}}", value)
    return out


def install(skill_dir: Path, stack_name: str, target_dir: Path) -> dict:
    """Run the install. Returns a report dict for verification."""
    stack_path = skill_dir / "references" / "stacks" / f"{stack_name}.md"
    values = parse_stack(stack_path)

    claude_tmpl = skill_dir / "assets" / "CLAUDE.md.tmpl"
    commands_dir = skill_dir / "assets" / "commands"
    seeds_dir = skill_dir / "assets" / "docs-seeds"

    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / ".claude" / "commands").mkdir(parents=True, exist_ok=True)
    (target_dir / "docs" / "architecture").mkdir(parents=True, exist_ok=True)

    written = []
    leftover_tokens: dict[str, list[str]] = {}

    def write_file(dest: Path, content: str) -> None:
        dest.write_text(content, encoding="utf-8")
        written.append(str(dest.relative_to(target_dir)))
        remaining = re.findall(r"\{\{[A-Z_][A-Z_0-9]*\}\}", content)
        if remaining:
            leftover_tokens[str(dest.relative_to(target_dir))] = sorted(set(remaining))

    claude_out = substitute(claude_tmpl.read_text(encoding="utf-8"), values)
    write_file(target_dir / "CLAUDE.md", claude_out)

    for cmd in sorted(commands_dir.glob("*.md")):
        out = substitute(cmd.read_text(encoding="utf-8"), values)
        write_file(target_dir / ".claude" / "commands" / cmd.name, out)

    for seed in sorted(seeds_dir.glob("*.md")):
        out = substitute(seed.read_text(encoding="utf-8"), values)
        write_file(target_dir / "docs" / "architecture" / seed.name, out)

    return {
        "values_parsed": list(values.keys()),
        "files_written": written,
        "leftover_tokens": leftover_tokens,
    }


if __name__ == "__main__":
    skill_dir = Path(sys.argv[1]).resolve()
    stack_name = sys.argv[2]
    target_dir = Path(sys.argv[3]).resolve()

    report = install(skill_dir, stack_name, target_dir)

    print(f"Parsed {len(report['values_parsed'])} placeholders from {stack_name}:")
    for token in report["values_parsed"]:
        print(f"  - {token}")
    print()
    print(f"Wrote {len(report['files_written'])} files to {target_dir}:")
    for path in report["files_written"]:
        print(f"  - {path}")
    print()
    if report["leftover_tokens"]:
        print("FAIL — files with unsubstituted tokens:")
        for path, tokens in report["leftover_tokens"].items():
            print(f"  - {path}: {tokens}")
        sys.exit(1)
    print("PASS — no unsubstituted tokens remain.")
