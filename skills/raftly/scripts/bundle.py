#!/usr/bin/env python3
"""Package a Raftly project as one zip file, and restore it.

For hosts with no lasting repository, such as the Claude apps, where the sandbox
is cleared between conversations. Export at the end of a turn and give the user
the zip; when they upload it again, import it and carry on.

  bundle.py export [--root DIR] [--out DIR]    write <out>/<project>-raftly.zip
                                               with .raftly/ and artifacts/
  bundle.py import <ZIP> [--root DIR] [--force]
                                               restore .raftly/ and artifacts/
                                               into the project folder

Import only accepts files under .raftly/ or artifacts/ (optionally inside one
top-level folder). It refuses absolute paths, "..", links and oversized
archives, and never overwrites an existing project unless --force is given.
"""

from __future__ import annotations

import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))

from forgelib import cli  # noqa: E402
from forgelib.brand import brand  # noqa: E402
from forgelib.fsutil import assert_not_plugin_core, resolve_inside, slugify  # noqa: E402
from forgelib.project import ForgeError  # noqa: E402

MAX_FILES = 5000
MAX_TOTAL_BYTES = 100 * 1024 * 1024


def _top_dirs() -> tuple[str, ...]:
    return (brand()["state_dir"], "artifacts")


def export(proj, out_dir: Path) -> dict:
    proj.require()
    name = (proj.state().get("project") or {}).get("name") or proj.root.name
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"{slugify(name) or 'project'}-raftly.zip"
    files = []
    for top in _top_dirs():
        base = proj.root / top
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_symlink() or not path.is_file():
                continue
            if target.resolve() == path.resolve():
                continue
            files.append(path)
    if len(files) > MAX_FILES:
        raise ForgeError(f"too many files to export ({len(files)} > {MAX_FILES})")
    tmp = target.with_name(target.name + ".tmp")
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            zf.write(path, path.relative_to(proj.root).as_posix())
    tmp.replace(target)
    return {"zip": str(target), "files": len(files), "bytes": target.stat().st_size}


def _members(zf: zipfile.ZipFile) -> list[tuple[zipfile.ZipInfo, PurePosixPath]]:
    """Validate every entry and map it to a path relative to the project root."""
    tops = _top_dirs()
    infos = [i for i in zf.infolist() if not i.is_dir()]
    if not infos:
        raise ForgeError("the zip is empty")
    if len(infos) > MAX_FILES:
        raise ForgeError(f"the zip has too many files ({len(infos)} > {MAX_FILES})")
    if sum(i.file_size for i in infos) > MAX_TOTAL_BYTES:
        raise ForgeError("the zip is too large once extracted")
    paths = []
    for info in infos:
        raw = info.filename.replace("\\", "/")
        p = PurePosixPath(raw)
        if p.is_absolute() or ".." in p.parts or (p.parts and ":" in p.parts[0]):
            raise ForgeError(f"unsafe path in zip: {info.filename}")
        if stat.S_ISLNK(info.external_attr >> 16):
            raise ForgeError(f"links are not allowed in the zip: {info.filename}")
        paths.append((info, p))
    # Accept a zip whose contents sit inside one wrapping folder (e.g. "my-app/.raftly/...").
    firsts = {p.parts[0] for _, p in paths if p.parts}
    if len(firsts) == 1 and next(iter(firsts)) not in tops:
        paths = [(i, PurePosixPath(*p.parts[1:])) for i, p in paths if len(p.parts) > 1]
    for info, p in paths:
        if not p.parts or p.parts[0] not in tops:
            raise ForgeError(f"not a Raftly project file: {info.filename} (expected {' or '.join(t + '/' for t in tops)})")
    if not any(p.parts[0] == tops[0] for _, p in paths):
        raise ForgeError(f"no {tops[0]}/ folder in the zip")
    return paths


def restore(proj, archive: Path, force: bool) -> dict:
    if not archive.is_file():
        raise ForgeError(f"no such file: {archive}")
    if proj.exists and not force:
        raise ForgeError(f"{proj.root} already has a {brand()['state_dir']}/ folder; pass --force to overwrite it")
    try:
        zf = zipfile.ZipFile(archive)
    except zipfile.BadZipFile as exc:
        raise ForgeError(f"not a zip file: {archive}") from exc
    with zf:
        members = _members(zf)
        written = 0
        for info, rel in members:
            dest = resolve_inside(proj.root, str(rel))
            assert_not_plugin_core(dest)
            dest.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as src:
                dest.write_bytes(src.read())
            written += 1
    return {"root": str(proj.root), "files": written}


def main(argv: list[str]) -> int:
    p = cli.parser("bundle.py", "Package or restore a Raftly project as a zip")
    sub = p.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("export")
    e.add_argument("--out", default=None, help="folder for the zip (default: the project root)")
    i = sub.add_parser("import")
    i.add_argument("zip")
    i.add_argument("--force", action="store_true")
    args = p.parse_args(argv)
    proj = cli.project(args)
    if args.cmd == "export":
        out = Path(args.out).expanduser().resolve() if args.out else proj.root
        res = export(proj, out)
        cli.emit(args, res, lambda d: f"Exported {d['files']} files to {d['zip']} ({d['bytes']:,} bytes).")
        return 0
    res = restore(proj, Path(args.zip).expanduser().resolve(), args.force)
    cli.emit(args, res, lambda d: f"Restored {d['files']} files into {d['root']}.")
    return 0


if __name__ == "__main__":
    cli.run(main)
