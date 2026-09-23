from dataclasses import dataclass, field


@dataclass
class DiffFile:
    path: str
    added_lines: list[str] = field(default_factory=list)
    removed_lines: list[str] = field(default_factory=list)


def parse_diff(raw: str) -> list[DiffFile]:
    """Minimal unified-diff parser: groups added/removed lines by file.

    This is intentionally simple to start with. Once you need to handle
    renames, binary files, or hunk-level line numbers, swap this out for
    the `unidiff` package rather than growing this by hand.
    """
    files: list[DiffFile] = []
    current: DiffFile | None = None

    for line in raw.splitlines():
        if line.startswith("+++ b/"):
            current = DiffFile(path=line[len("+++ b/") :])
            files.append(current)
        elif current is not None and line.startswith("+") and not line.startswith("+++"):
            current.added_lines.append(line[1:])
        elif current is not None and line.startswith("-") and not line.startswith("---"):
            current.removed_lines.append(line[1:])

    return files
