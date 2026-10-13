#!/usr/bin/env python3
"""Convert code files under the project root to UTF-8 without changing newlines.

From the project root, run: python tools/convert_project_to_utf8.py

The script scans the project root (the parent of this script's tools folder).
Changed originals are backed up under the project root's backup/ folder.
"""

from __future__ import annotations

import codecs
import os
import shutil
import sys
import tempfile
from pathlib import Path


SOURCE_ENCODING = "gb18030"  # Change here if legacy files use another encoding.
BACKUP_ORIGINALS = True  # Save changed originals as .bak files under backup/.
BACKUP_DIR_NAME = "backup"


CODE_EXTENSIONS = {
    ".c", ".h", ".cc", ".cpp", ".cxx", ".hpp", ".hxx",
    ".s", ".asm", ".inc", ".ino", ".py", ".rs", ".go",
    ".java", ".js", ".ts", ".ld", ".lds", ".dts", ".dtsi",
    ".cmake", ".mk", ".mak", ".sh", ".bat", ".cmd", ".ps1",
    ".json", ".xml", ".yaml", ".yml", ".toml", ".ini",
    ".cfg", ".conf", ".def", ".ioc", ".uvprojx", ".uvoptx",
    ".ewp", ".eww", ".icf", ".sct",
}
CODE_NAMES = {"makefile", "gnumakefile", "cmakelists.txt", "kconfig", "dockerfile"}
SKIP_DIRS = {".git", ".hg", ".svn", ".venv", "venv", "__pycache__", BACKUP_DIR_NAME,
             "build", "dist", "out", "objects", "listings", ".idea", ".vscode"}
BOMS = (
    (codecs.BOM_UTF32_LE, "utf-32"),
    (codecs.BOM_UTF32_BE, "utf-32"),
    (codecs.BOM_UTF8, "utf-8-sig"),
    (codecs.BOM_UTF16_LE, "utf-16"),
    (codecs.BOM_UTF16_BE, "utf-16"),
)


def source_text(data: bytes, fallback: str) -> tuple[str, str]:
    for bom, encoding in BOMS:
        if data.startswith(bom):
            return data.decode(encoding), encoding
    if b"\x00" in data:
        raise ValueError("contains NUL bytes (binary or Unicode without BOM)")
    try:
        return data.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        return data.decode(fallback), fallback


def atomic_write(path: Path, data: bytes) -> None:
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=path.parent,
                                         prefix=f".{path.name}.", suffix=".tmp",
                                         delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        shutil.copymode(path, temporary)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def code_files(root: Path):
    for folder, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = [name for name in dirs
                   if name.lower() not in SKIP_DIRS
                   and not (Path(folder) / name).is_symlink()]
        for name in names:
            path = Path(folder) / name
            if not path.is_symlink() and (
                path.suffix.lower() in CODE_EXTENSIONS or name.lower() in CODE_NAMES
            ):
                yield path


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    try:
        codecs.lookup(SOURCE_ENCODING)
    except LookupError:
        print(f"Unknown source encoding: {SOURCE_ENCODING}", file=sys.stderr)
        return 2

    changed = unchanged = skipped = 0
    print(f"Scanning: {root}")
    for path in code_files(root):
        relative = path.relative_to(root)
        try:
            original = path.read_bytes()
            decoded, encoding = source_text(original, SOURCE_ENCODING)
            converted = decoded.encode("utf-8")  # UTF-8 without BOM; preserves newline characters
            if converted == original:
                unchanged += 1
                continue
            if BACKUP_ORIGINALS:
                backup = root / BACKUP_DIR_NAME / relative.parent / (path.name + ".bak")
                if backup.exists():
                    raise FileExistsError(f"backup already exists: {backup}")
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, backup)
            atomic_write(path, converted)
            print(f"CONVERT {relative} ({encoding} -> utf-8)")
            changed += 1
        except (OSError, UnicodeError, ValueError) as exc:
            skipped += 1
            print(f"SKIP {relative}: {exc}", file=sys.stderr)

    print(f"Summary: {changed} changed, {unchanged} already UTF-8, {skipped} skipped")
    return 1 if skipped else 0


if __name__ == "__main__":
    raise SystemExit(main())
