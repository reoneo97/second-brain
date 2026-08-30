"""Low-level vault I/O: parse and write OKF Markdown (YAML frontmatter + body).

Mechanical only — no task or scheduling logic here.
"""
import re
from pathlib import Path
import yaml

# Match frontmatter delimited by `---` on their OWN lines (so `---` inside YAML
# comments or note-body horizontal rules doesn't false-trigger).
_FM_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.S)


def parse_note(path: Path) -> tuple[dict, str]:
    """Return (frontmatter dict, body str). Empty dict if no frontmatter."""
    text = path.read_text(encoding="utf-8")
    m = _FM_RE.match(text)
    if m:
        return yaml.safe_load(m.group(1)) or {}, m.group(2).lstrip("\n")
    return {}, text


class _CleanDumper(yaml.SafeDumper):
    """Emit empty (not `null`) for None, so blank OKF fields stay blank."""


_CleanDumper.add_representer(
    type(None),
    lambda d, _: d.represent_scalar("tag:yaml.org,2002:null", ""),
)


def write_atomic(path: Path, text: str) -> None:
    """Write raw text atomically (temp file + replace)."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def write_note(path: Path, frontmatter: dict, body: str) -> None:
    """Write an OKF note atomically. Preserves key order; keeps unicode (emojis).

    NOTE: this re-emits the whole frontmatter (YAML dump), so it can shift line
    numbers. Callers that address content by line (steps) must edit in place
    instead — see tasks.update_task."""
    fm = yaml.dump(frontmatter, Dumper=_CleanDumper, sort_keys=False,
                   allow_unicode=True).rstrip("\n")
    write_atomic(path, f"---\n{fm}\n---\n\n{body.strip()}\n")
