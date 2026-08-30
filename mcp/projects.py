"""Read an external project's Claude memory as a sync feed.

Deliberately a **dumb pipe**: it resolves the memory dir a container declares
(`memory:` in its frontmatter), reads `MEMORY.md` + each memory file, and returns
loose {name, description, type, modified, body} blobs. It does NOT interpret them
— the sync-project skill (an LLM) does that, so schema drift in Claude Code's
memory format degrades to "just read the prose" instead of breaking a parser.

Stable anchors only: frontmatter delimiters + `description` + body; `type` and
`modified` are read from either the top level or a nested `metadata:` map when
present, and are optional.
"""
from pathlib import Path

import tasks
from vault import parse_note


def _memory_dir(project_id=None, memory_path=None) -> Path | None:
    if memory_path:
        return Path(memory_path).expanduser()
    if project_id:
        for _p, fm, _ in tasks._iter_containers():
            if fm.get("id") == project_id and fm.get("memory"):
                return Path(str(fm["memory"])).expanduser()
    return None


def read_project_status(project_id: str | None = None,
                        memory_path: str | None = None) -> dict:
    """Read a linked project's memory. Pass a container `project_id` (uses its
    `memory:` field) or an explicit `memory_path`. Returns the raw MEMORY.md
    index text + a list of memory blobs — no interpretation."""
    d = _memory_dir(project_id, memory_path)
    if not d or not d.exists():
        return {"memory_dir": str(d) if d else None, "found": False,
                "index": None, "memories": []}
    index = (d / "MEMORY.md").read_text(encoding="utf-8") \
        if (d / "MEMORY.md").exists() else None
    memories = []
    for f in sorted(d.glob("*.md")):
        if f.name == "MEMORY.md":
            continue
        fm, body = parse_note(f)
        meta = fm.get("metadata") if isinstance(fm.get("metadata"), dict) else {}
        memories.append({
            "file": f.name,
            "name": fm.get("name"),
            "description": fm.get("description"),
            "type": fm.get("type") or meta.get("type"),
            "modified": meta.get("modified") or fm.get("modified"),
            "body": body.strip(),
        })
    return {"memory_dir": str(d), "found": True, "index": index,
            "memories": memories}
