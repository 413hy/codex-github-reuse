#!/usr/bin/env python3
"""Install the bundled Codex skill and its managed AGENTS rule (Python 3.9+)."""

import argparse
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import tempfile
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple
from uuid import uuid4


SKILL_NAME = "github-reuse-first"
START = b"<!-- github-reuse-first:start -->"
END = b"<!-- github-reuse-first:end -->"
UTF8_BOM = b"\xef\xbb\xbf"
# Rust str::trim uses Unicode White_Space. Python str.strip additionally strips
# U+001C-U+001F, so use the same explicit character set as the Codex loader.
UNICODE_WHITE_SPACE = (
    "\t\n\v\f\r \u0085\u00a0\u1680"
    "\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a"
    "\u2028\u2029\u202f\u205f\u3000"
)


class InstallError(Exception):
    """An actionable error detected before replacing user files."""


def absolute(path: Path) -> Path:
    # abspath normalizes '..' without following a symlink before we inspect it.
    return Path(os.path.abspath(os.fspath(path.expanduser())))


def reject_links(path: Path) -> None:
    """Do not write through symlinked or junction-based installation paths."""
    for item in (path, *path.parents):
        if item.is_symlink():
            raise InstallError("Refusing symbolic-link path: {}".format(item))
        junction_check = getattr(item, "is_junction", None)
        if junction_check is not None and junction_check():
            raise InstallError("Refusing junction path: {}".format(item))
        # is_junction is unavailable in Python 3.9-3.11 on Windows.
        if os.name == "nt" and item.exists():
            info = item.lstat()
            if getattr(info, "st_file_attributes", 0) & 0x400:
                raise InstallError("Refusing reparse-point path: {}".format(item))


def read_file(path: Path) -> Optional[bytes]:
    reject_links(path)
    if not path.exists():
        return None
    if not path.is_file():
        raise InstallError("Expected a regular file: {}".format(path))
    return path.read_bytes()


def read_tree(path: Path) -> Optional[Dict[str, bytes]]:
    reject_links(path)
    if not path.exists():
        return None
    if not path.is_dir():
        raise InstallError("Expected a directory: {}".format(path))
    result = {}
    for item in sorted(path.rglob("*")):
        reject_links(item)
        if item.is_file():
            result[item.relative_to(path).as_posix()] = item.read_bytes()
        elif not item.is_dir():
            raise InstallError("Unsupported file type: {}".format(item))
    return result


def marker_span(data: bytes) -> Optional[Tuple[int, int]]:
    """Return the one well-formed managed block; reject damaged markers."""
    starts, ends = data.count(START), data.count(END)
    prefixes = len(re.findall(rb"<!--\s*github-reuse-first\b", data, flags=re.IGNORECASE))
    if not starts and not ends and not prefixes:
        return None
    if starts != 1 or ends != 1 or prefixes != 2:
        raise InstallError("Duplicate or incomplete github-reuse-first markers; fix them first.")
    first, last = data.index(START), data.index(END)
    if last < first + len(START):
        raise InstallError("The github-reuse-first end marker precedes its start marker.")
    for offset, marker in ((first, START), (last, END)):
        line_start = data.rfind(b"\n", 0, offset) + 1
        before = data[line_start:offset]
        if line_start == 0 and before.startswith(UTF8_BOM):
            before = before[len(UTF8_BOM):]
        line_end = data.find(b"\n", offset + len(marker))
        if line_end == -1:
            line_end = len(data)
        after = data[offset + len(marker):line_end]
        if before.strip() or after.strip():
            raise InstallError("Managed markers must be on their own lines.")
    return first, last + len(END)


def merge_rule(existing: bytes, template: bytes) -> bytes:
    try:
        existing.decode("utf-8-sig")
        template.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise InstallError("AGENTS files must use UTF-8 (a UTF-8 BOM is supported).") from exc

    template = template.removeprefix(UTF8_BOM)
    source_span = marker_span(template)
    if source_span is None:
        raise InstallError("The bundled rule template has no managed block.")
    first, last = source_span
    if template[:first].strip() or template[last:].strip():
        raise InstallError("The rule template contains text outside its managed block.")
    block = template[first:last].replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    first_newline = existing.find(b"\n")
    newline = b"\r\n" if first_newline > 0 and existing[first_newline - 1:first_newline] == b"\r" else b"\n"
    block = block.replace(b"\n", newline)
    old_span = marker_span(existing)
    if old_span is not None:
        first, last = old_span
        return existing[:first] + block + existing[last:]

    body = existing.removeprefix(UTF8_BOM)
    if not body:
        return existing + block + newline
    if existing.endswith(newline * 2):
        separator = b""
    elif existing.endswith(newline):
        separator = newline
    else:
        separator = newline * 2
    return existing + separator + block + newline


def active_rule_path(directory: Path, *, scope: str) -> Path:
    """Match Codex's distinct project and global override selection rules."""
    override = directory / "AGENTS.override.md"
    data = read_file(override)
    if data is not None:
        # Project discovery selects an existing file before reading its content.
        if scope == "project":
            return override
        # Global discovery skips Unicode-whitespace-only text, but retains BOM.
        if data.decode("utf-8", errors="replace").strip(UNICODE_WHITE_SPACE):
            return override
    return directory / "AGENTS.md"


def overlaps(left: Path, right: Path) -> bool:
    return left == right or left in right.parents or right in left.parents


def backup_name(path: Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return path.with_name(path.name + ".bak-" + stamp + "-" + uuid4().hex[:8])


def atomic_write(path: Path, data: bytes) -> None:
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else None
    handle, name = tempfile.mkstemp(prefix="." + path.name + ".", dir=str(path.parent))
    temporary = Path(name)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if mode is not None:
            temporary.chmod(mode)
        os.replace(str(temporary), str(path))
    finally:
        if temporary.exists():
            temporary.unlink()


def install(package_dir: Path, *, project: Optional[Path] = None,
            update: bool = False, dry_run: bool = False) -> dict:
    """Preflight, back up changed installations, and install without executing content.

    ``update`` remains accepted for compatibility; backing up and updating an
    existing installation is now the default.
    """
    package_dir = absolute(package_dir)
    source = package_dir / "skills" / SKILL_NAME
    source_files = read_tree(source)
    if not source_files or "SKILL.md" not in source_files:
        raise InstallError("The package is missing skills/{}/SKILL.md.".format(SKILL_NAME))
    rule_source = package_dir / "rules" / "AGENTS.github-reuse.md"
    template = read_file(rule_source)
    if template is None:
        raise InstallError("The package is missing rules/AGENTS.github-reuse.md.")

    if project is not None:
        project = absolute(project)
        reject_links(project)
        if not project.is_dir():
            raise InstallError("--project must name an existing project directory.")
        destination = project / ".agents" / "skills" / SKILL_NAME
        rule_directory = project
        scope = "project"
    else:
        home = absolute(Path.home())
        destination = home / ".agents" / "skills" / SKILL_NAME
        codex_home = os.environ.get("CODEX_HOME")
        rule_directory = absolute(Path(codex_home)) if codex_home else home / ".codex"
        scope = "global"

    rule_path = active_rule_path(rule_directory, scope=scope)
    for target in (destination, rule_path):
        reject_links(target)
        if overlaps(target, source) or overlaps(target, rule_source):
            raise InstallError("An installation target overlaps its bundled source: {}".format(target))
        for parent in target.parents:
            if parent.exists() and not parent.is_dir():
                raise InstallError("A destination parent is not a directory: {}".format(parent))

    old_skill = read_tree(destination)
    old_rule = read_file(rule_path)
    new_rule = merge_rule(old_rule or b"", template)
    skill_changed = old_skill != source_files
    rule_changed = old_rule != new_rule
    # Keep old SKILL.md files outside the directory Codex scans for skills.
    backup_directory = destination.parent.parent / "skill-backups"
    if old_skill is not None and skill_changed:
        reject_links(backup_directory)
        if backup_directory.exists() and not backup_directory.is_dir():
            raise InstallError("The skill backup location is not a directory: {}".format(backup_directory))

    result = {
        "scope": scope, "skill_path": str(destination), "rule_path": str(rule_path),
        "skill_changed": skill_changed, "rule_changed": rule_changed,
        "dry_run": dry_run, "backups": [],
    }
    if dry_run or not (skill_changed or rule_changed):
        return result

    # Recheck before any write if another process changed the chosen targets.
    if read_tree(destination) != old_skill or read_file(rule_path) != old_rule:
        raise InstallError("A destination changed during preflight; re-run the installer.")
    if active_rule_path(rule_directory, scope=scope) != rule_path:
        raise InstallError("The active AGENTS file changed during preflight; re-run the installer.")

    stage = None
    skill_backup = None
    skill_installed = False
    try:
        if skill_changed:
            destination.parent.mkdir(parents=True, exist_ok=True)
            stage = Path(tempfile.mkdtemp(prefix=".github-reuse-first-stage-", dir=str(destination.parent)))
            for relative, content in source_files.items():
                staged_file = stage / relative
                staged_file.parent.mkdir(parents=True, exist_ok=True)
                staged_file.write_bytes(content)
            if old_skill is not None:
                backup_directory.mkdir(parents=True, exist_ok=True)
                skill_backup = backup_directory / backup_name(destination).name
                os.replace(str(destination), str(skill_backup))
            os.replace(str(stage), str(destination))
            stage = None
            skill_installed = True
        if rule_changed:
            rule_path.parent.mkdir(parents=True, exist_ok=True)
            if old_rule is not None:
                rule_backup = backup_name(rule_path)
                shutil.copy2(str(rule_path), str(rule_backup))
                result["backups"].append(str(rule_backup))
            atomic_write(rule_path, new_rule)
        if skill_backup is not None:
            result["backups"].insert(0, str(skill_backup))
    except Exception:
        # A rules-write failure must not leave the user with a replaced skill.
        if skill_installed:
            shutil.rmtree(str(destination))
        if skill_backup is not None and skill_backup.exists():
            os.replace(str(skill_backup), str(destination))
        raise
    finally:
        if stage is not None and stage.exists():
            shutil.rmtree(str(stage))
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--global", dest="global_scope", action="store_true",
                       help="Install for the current user across projects (default).")
    scope.add_argument("--project", type=Path, metavar="PATH",
                       help="Install only in an existing project directory.")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing any files.")
    parser.add_argument("--update", action="store_true",
                        help="Compatibility option: backup and update are already the default.")
    args = parser.parse_args(argv)
    try:
        result = install(Path(__file__).parent, project=args.project,
                         update=args.update, dry_run=args.dry_run)
    except (InstallError, OSError) as exc:
        print("ERROR: {}".format(exc), file=sys.stderr)
        return 2
    label = "DRY RUN" if args.dry_run else "OK"
    print("{}: {} installation".format(label, result["scope"]))
    print("Skill: {} [{}]".format(result["skill_path"], "change" if result["skill_changed"] else "unchanged"))
    print("Rules: {} [{}]".format(result["rule_path"], "change" if result["rule_changed"] else "unchanged"))
    for path in result["backups"]:
        print("Backup: {}".format(path))
    if args.dry_run:
        print("No files were written.")
    else:
        print("Start a new Codex session. Use /skills or mention $github-reuse-first to verify discovery.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
