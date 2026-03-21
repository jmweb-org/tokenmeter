"""Gather text inputs from files, directories, or standard input."""

from __future__ import annotations

import sys
from collections.abc import Iterable, Sequence
from pathlib import Path

TEXT_SUFFIXES = {".txt", ".md", ".prompt", ".jinja", ".j2", ".tmpl"}


def read_inputs(
    paths: Sequence[str | Path],
    *,
    stdin_text: str | None = None,
) -> list[tuple[str, str]]:
    """Return ``(name, text)`` pairs for every requested input.

    A path of ``-`` reads standard input. Directories are expanded to their
    text-like files, sorted for stable output.
    """

    out: list[tuple[str, str]] = []
    for raw in paths:
        if str(raw) == "-":
            text = stdin_text if stdin_text is not None else sys.stdin.read()
            out.append(("<stdin>", text))
            continue
        path = Path(raw)
        if path.is_dir():
            for child in _text_files(path):
                out.append((str(child), child.read_text(encoding="utf-8")))
        else:
            out.append((str(path), path.read_text(encoding="utf-8")))
    return out


def _text_files(directory: Path) -> Iterable[Path]:
    return sorted(
        p for p in directory.rglob("*") if p.is_file() and p.suffix.lower() in TEXT_SUFFIXES
    )
