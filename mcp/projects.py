"""Read an external project's status contract as a sync feed.

Deliberately a **dumb pipe**: it resolves the repo a container declares
(`repo:` in its frontmatter) and reads a small git-tracked status file inside
it (`status_file:`, default `.second-brain/status.md`) — frontmatter + body,
no interpretation. The sync-project skill (an LLM) does the interpreting, so
drift in how a given project phrases its status degrades to "just read the
prose" instead of breaking a parser.

Why a git-tracked file instead of Claude Code's own `~/.claude/projects/.../
memory/` dir (the original ADR-011 design): that memory is machine-local and
tied to whichever harness wrote it. A file committed in the project's own repo
travels via that repo's git remote, so `/sync-project` sees current status
regardless of which machine ran the last session or which agent harness
(Claude Code today, a future Hermes harness, ...) wrote it. See ADR-015.
"""
from pathlib import Path

import tasks
from vault import parse_note

DEFAULT_STATUS_FILE = ".second-brain/status.md"


def _status_path(project_id=None, repo_path=None, status_file=None) -> Path | None:
    if repo_path:
        repo = Path(repo_path).expanduser()
        return repo / (status_file or DEFAULT_STATUS_FILE)
    if project_id:
        for _p, fm, _ in tasks._iter_containers():
            if fm.get("id") == project_id and fm.get("repo"):
                repo = Path(str(fm["repo"])).expanduser()
                return repo / str(fm.get("status_file") or DEFAULT_STATUS_FILE)
    return None


def read_project_status(project_id: str | None = None,
                        repo_path: str | None = None,
                        status_file: str | None = None) -> dict:
    """Read a linked project's status file. Pass a container `project_id`
    (uses its `repo:` + optional `status_file:` fields) or an explicit
    `repo_path`. Returns the raw frontmatter + body — no interpretation."""
    p = _status_path(project_id, repo_path, status_file)
    if not p or not p.exists():
        return {"status_file": str(p) if p else None, "found": False,
                "frontmatter": None, "body": None}
    fm, body = parse_note(p)
    return {"status_file": str(p), "found": True, "frontmatter": fm,
            "body": body.strip()}
