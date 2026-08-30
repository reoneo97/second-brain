"""Container/step task access over the canonical `type: task` files.

Two levels of granularity:

- **Container** = one `type: task` file. Frontmatter holds the shared
  classification (cycle, roadmap, category, quarter, priority) + a `status`
  rollup for the whole phase. Identified by its uuid `id`.
- **Step** = a `- [ ]` checkbox line in the body. The atomic, schedulable,
  completable unit. Identified by `"<relative/path.md>:<1-based line>"` — the
  same id the Time Blocks plugin uses. Inherits its container's classification.

Per-step metadata lives inline (no YAML on a checkbox): `[size:: S|M|L]`, an
Obsidian-Tasks `📅 YYYY-MM-DD` due date, and a trailing `[↗](url)` resource.

Mechanical only — the plan-day skill does the scheduling reasoning.
"""
import datetime
import re
import uuid
from pathlib import Path

import config
from vault import parse_note, write_note, write_atomic

# a markdown task checkbox:  "  - [ ] text"  /  "- [x] text"
_CHECKBOX_RE = re.compile(r"^(?P<indent>\s*)- \[(?P<mark>[ xX])\]\s+(?P<text>.*)$")
_SIZE_RE = re.compile(r"\[size::\s*([SMLsml])\]")
_DUE_RE = re.compile(r"📅\s*(\d{4}-\d{2}-\d{2})")
_LINK_RE = re.compile(r"\[[^\]]*\]\((https?://[^)]+)\)")

# container frontmatter fields a step inherits as context
_INHERIT = ("status", "category", "priority", "roadmap", "cycle", "quarter")


def _rel(p: Path) -> str:
    return str(p.relative_to(config.VAULT))


def _iter_containers():
    """Yield (path, frontmatter, body) for every `type: task` file."""
    if not config.TASKS_DIR.exists():
        return
    for p in sorted(config.TASKS_DIR.glob("*.md")):
        if p.name == "_index.md":
            continue
        fm, body = parse_note(p)
        if fm.get("type") == "task":
            yield p, fm, body


def _body_start_line(path: Path) -> int:
    """1-based line number where the body begins (line after the closing `---`)."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return 1
    lines = text.split("\n")
    # find the SECOND '---' delimiter line; body starts on the next line
    seen = 0
    for i, ln in enumerate(lines):
        if ln.strip() == "---":
            seen += 1
            if seen == 2:
                return i + 2  # 1-based line after the delimiter
    return 1


def _parse_step_text(text: str):
    """Split a checkbox's text into (clean_title, size, due, resource)."""
    size = None
    m = _SIZE_RE.search(text)
    if m:
        size = m.group(1).upper()
        text = _SIZE_RE.sub("", text)
    due = None
    m = _DUE_RE.search(text)
    if m:
        due = m.group(1)
        text = _DUE_RE.sub("", text)
    resource = None
    m = _LINK_RE.search(text)
    if m:
        resource = m.group(1)
        text = _LINK_RE.sub("", text)
    return re.sub(r"\s+", " ", text).strip(), size, due, resource


def _format_step(indent: str, done: bool, title: str,
                 size=None, due=None, resource=None) -> str:
    line = f"{indent}- [{'x' if done else ' '}] {title}"
    if size:
        line += f" [size:: {size}]"
    if due:
        line += f" 📅 {due}"
    if resource:
        line += f" [↗]({resource})"
    return line


def _steps_in(path: Path, fm: dict) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    rel = _rel(path)
    ctx = {"project": fm.get("title"), "project_id": fm.get("id"),
           **{k: fm.get(k) for k in _INHERIT}}
    out = []
    for i, raw in enumerate(text.split("\n"), start=1):
        m = _CHECKBOX_RE.match(raw)
        if not m:
            continue
        title, size, due, resource = _parse_step_text(m.group("text"))
        out.append({
            "id": f"{rel}:{i}", "path": rel, "line": i,
            "title": title, "size": size,
            "done": m.group("mark").lower() == "x",
            "due": due, "resource": resource,
            **ctx,
        })
    return out


# ---- steps (the schedulable units) -----------------------------------------
def list_tasks(status=None, done=None, cycle=None, roadmap=None,
               quarter=None, project=None) -> list[dict]:
    """List step checkboxes across all container files, with inherited context.

    Filters (any left None is ignored):
      status  — container status rollup (Backlog/Not started/In progress/Done)
      done    — step completion (False = only unchecked, the planner default)
      cycle / roadmap / quarter — inherited container classification
      project — container id (uuid) or a substring of its title
    """
    out = []
    for p, fm, _ in _iter_containers():
        if status and fm.get("status") != status:
            continue
        if cycle and fm.get("cycle") != cycle:
            continue
        if roadmap and fm.get("roadmap") != roadmap:
            continue
        if quarter and fm.get("quarter") != quarter:
            continue
        if project and project not in (fm.get("id"), ) and \
                project.lower() not in str(fm.get("title", "")).lower():
            continue
        for s in _steps_in(p, fm):
            if done is not None and s["done"] != done:
                continue
            out.append(s)
    return out


def get_task(task_id: str) -> dict | None:
    """One step by `"<path>:<line>"`. Also accepts a container uuid — returns
    its first unchecked step (or first step) as a convenience."""
    if ":" in task_id:
        path_part, _, line_part = task_id.rpartition(":")
        p = config.VAULT / path_part
        if p.exists() and line_part.isdigit():
            fm, _ = parse_note(p)
            for s in _steps_in(p, fm):
                if s["line"] == int(line_part):
                    return s
        return None
    # uuid fallback
    for p, fm, _ in _iter_containers():
        if fm.get("id") == task_id:
            steps = _steps_in(p, fm)
            todo = [s for s in steps if not s["done"]]
            return (todo or steps or [None])[0]
    return None


def update_task(task_id: str, fields: dict) -> dict | None:
    """Patch a step's checkbox line. Recognised fields: `done` (bool),
    `size` (S/M/L), `due` (YYYY-MM-DD), `title`, `resource`.

    Edits ONLY the target line (and the frontmatter `timestamp` line) in place —
    never reflows the file — so every step id / Time Blocks taskId stays valid."""
    if ":" not in task_id:
        return None
    path_part, _, line_part = task_id.rpartition(":")
    p = config.VAULT / path_part
    if not (p.exists() and line_part.isdigit()):
        return None
    lineno = int(line_part)
    lines = p.read_text(encoding="utf-8").split("\n")
    if not (1 <= lineno <= len(lines)):
        return None
    m = _CHECKBOX_RE.match(lines[lineno - 1])
    if not m:
        return None
    title, size, due, resource = _parse_step_text(m.group("text"))
    done = m.group("mark").lower() == "x"
    lines[lineno - 1] = _format_step(
        m.group("indent"),
        bool(fields.get("done", done)),
        fields.get("title", title),
        fields.get("size", size),
        fields.get("due", due),
        fields.get("resource", resource),
    )
    # bump the container's timestamp in place (same line count → stable ids)
    today = datetime.date.today().isoformat()
    for i, ln in enumerate(lines[:_body_start_line(p)]):
        if ln.startswith("timestamp:"):
            lines[i] = f"timestamp: {today}"
            break
    write_atomic(p, "\n".join(lines))
    return get_task(task_id)


# ---- containers (phases / projects; for cycle planning + sync) -------------
def list_projects(status=None, cycle=None, roadmap=None, quarter=None) -> list[dict]:
    """List container files (frontmatter + path), with a done/total step count."""
    out = []
    for p, fm, _ in _iter_containers():
        if status and fm.get("status") != status:
            continue
        if cycle and fm.get("cycle") != cycle:
            continue
        if roadmap and fm.get("roadmap") != roadmap:
            continue
        if quarter and fm.get("quarter") != quarter:
            continue
        steps = _steps_in(p, fm)
        out.append({**fm, "path": _rel(p), "line": 2,
                    "steps_total": len(steps),
                    "steps_done": sum(s["done"] for s in steps)})
    return out


def _fmt_scalar(v) -> str:
    if v is None or v == "":
        return ""
    if isinstance(v, (list, tuple)):
        return "[" + ", ".join(str(x) for x in v) + "]"
    s = str(v)
    return f'"{s}"' if (":" in s or s != s.strip()) else s


def _set_fm_line(lines: list[str], fm_end: int, key: str, value) -> bool:
    """Replace an existing `key:` line within the frontmatter, in place. Returns
    False if the key isn't present (caller decides whether to append)."""
    for i in range(1, fm_end):
        if lines[i].startswith(f"{key}:"):
            val = _fmt_scalar(value)
            lines[i] = f"{key}:{' ' + val if val else ''}"
            return True
    return False


def add_step(project_id: str, title: str, size: str | None = None,
             due: str | None = None, resource: str | None = None) -> dict | None:
    """Append a new step checkbox to a container, after its last existing step
    (so no existing step id / block shifts). Creates a `## Steps` section if the
    file has none. Bumps the container timestamp."""
    for p, fm, _ in _iter_containers():
        if fm.get("id") != project_id:
            continue
        lines = p.read_text(encoding="utf-8").split("\n")
        new = _format_step("", False, title, size, due, resource)
        last_cb = max((i for i, ln in enumerate(lines) if _CHECKBOX_RE.match(ln)),
                      default=None)
        hdr = next((i for i, ln in enumerate(lines)
                    if ln.strip().lower() == "## steps"), None)
        if last_cb is not None:
            lines.insert(last_cb + 1, new); ins = last_cb + 2
        elif hdr is not None:
            lines.insert(hdr + 1, new); ins = hdr + 2
        else:
            if lines and lines[-1].strip():
                lines.append("")
            lines += ["## Steps", new]; ins = len(lines)
        for i in range(_body_start_line(p)):
            if lines[i].startswith("timestamp:"):
                lines[i] = f"timestamp: {datetime.date.today().isoformat()}"
                break
        write_atomic(p, "\n".join(lines))
        return get_task(f"{_rel(p)}:{ins}")
    return None


def update_project(project_id: str, fields: dict) -> dict | None:
    """Patch a container's frontmatter (status, start_week, notion_id, …) by its
    uuid, in place — never reflows the body, so step line ids stay valid. Keys
    not already in the frontmatter are appended just before the closing `---`."""
    for p, fm, _ in _iter_containers():
        if fm.get("id") != project_id:
            continue
        lines = p.read_text(encoding="utf-8").split("\n")
        fm_end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), 1)
        patch = {**fields, "timestamp": datetime.date.today().isoformat()}
        for k, v in patch.items():
            if not _set_fm_line(lines, fm_end, k, v):
                val = _fmt_scalar(v)
                lines.insert(fm_end, f"{k}:{' ' + val if val else ''}")
                fm_end += 1
        write_atomic(p, "\n".join(lines))
        new_fm, _ = parse_note(p)
        return {**new_fm, "path": _rel(p), "line": 2}
    return None


def create_project(fields: dict, body: str = "") -> dict:
    """Create a new container `type: task` file. Mints id + timestamp."""
    fm = {"type": "task", "id": str(uuid.uuid4()), **fields}
    fm.setdefault("status", "Backlog")
    fm["timestamp"] = datetime.date.today().isoformat()
    slug = fm.get("title", fm["id"]).lower().replace(" ", "-")[:60]
    config.TASKS_DIR.mkdir(parents=True, exist_ok=True)
    p = config.TASKS_DIR / f"{slug}.md"
    write_note(p, fm, body or fm.get("title", ""))
    return {**fm, "path": _rel(p), "line": 2}
