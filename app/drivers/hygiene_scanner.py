"""hygiene_scanner — a real local code-issue SOURCE for the Self-Healing lane.

The lineage / eval feed carries no code-fix signals yet, so this is the first
genuine producer: walk a repo, find files with deterministic hygiene issues
(trailing whitespace, missing trailing newline), and shape ONE concrete code-fix
proposal per file via ``CodeFixShaper.shape_all``. It is the "analysis" half of
the healing worker; the publisher then emits each proposal to DataForge-Local for
operator Accept/Reject.

Bounded + safe: text files only, skips VCS/build/cache dirs, caps file size and
(optionally) proposal count. READ-ONLY — never writes the repo; applying a fix is
the operator's explicit, downstream step.
"""
from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

from app.services.code_fix_shaper import CodeFixProposal, CodeFixShaper

_SKIP_DIRS = {
    ".git", ".hg", "node_modules", "target", "__pycache__", ".venv", "venv",
    "dist", "build", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".idea",
}
_TEXT_SUFFIXES = {
    ".py", ".rs", ".ts", ".tsx", ".js", ".svelte", ".md", ".toml", ".sh",
    ".json", ".yaml", ".yml", ".sql", ".txt", ".cfg", ".ini",
}
_MAX_BYTES = 512 * 1024  # skip files larger than 512 KiB


def _iter_text_files(root: Path) -> Iterator[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        for name in filenames:
            path = Path(dirpath) / name
            if path.suffix.lower() not in _TEXT_SUFFIXES:
                continue
            try:
                if path.stat().st_size > _MAX_BYTES:
                    continue
            except OSError:
                continue
            yield path


def scan_repo_for_hygiene_fixes(
    repo_root: str | Path,
    repository: str,
    *,
    commit_sha: str = "working-tree",
    max_proposals: int | None = None,
) -> list[CodeFixProposal]:
    """Scan ``repo_root`` read-only; return one hygiene proposal per fixable file."""
    root = Path(repo_root)
    shaper = CodeFixShaper()
    proposals: list[CodeFixProposal] = []
    for path in _iter_text_files(root):
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue  # not utf-8 text / unreadable
        rel = path.relative_to(root).as_posix()
        proposal = shaper.shape_all(repository, rel, content, commit_sha=commit_sha)
        if proposal is not None:
            proposals.append(proposal)
            if max_proposals is not None and len(proposals) >= max_proposals:
                break
    return proposals
