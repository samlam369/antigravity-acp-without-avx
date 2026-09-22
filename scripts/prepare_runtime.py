#!/usr/bin/env python3
"""Prepare a local pinned payload. Does not install packages or change a client."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import stat
import tempfile
import zipfile

PROJECT = Path(__file__).resolve().parents[1]
MANIFEST = PROJECT / "manifests" / "agy-acp-1.1.1-linux-x86_64.json"


def verify_file(path, expected):
    if "bytes" in expected and path.stat().st_size != expected["bytes"]:
        raise ValueError(f"Unexpected size: {path.name}")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    if digest.hexdigest() != expected["sha256"]:
        raise ValueError(f"SHA-256 mismatch: {path.name}")


def safe_member(name):
    """Reject ambiguous/escaping archive names before writing any payload."""
    path = PurePosixPath(name)
    if (not name or path.is_absolute() or ".." in path.parts
            or "\\" in name or ":" in name or "\x00" in name):
        raise ValueError(f"Unsafe archive member: {name!r}")
    return path


def mapped_source(name):
    prefix = "google3/third_party/py/"
    if name.startswith(prefix):
        short = name[len(prefix):]
        if short.endswith(".py") and short.startswith(("google/antigravity/", "acp/")):
            return short
        return None
    if (name.endswith(".py")
            or name.endswith("cloudcode-pa_prod_google_rest_v1internal.json")
            or "/acp_server/baic_connection/templates/" in name
            or name.endswith("agy_acp_licenses.txt")):
        return name
    return None


def extract_sources(par, destination):
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite: {destination}")
    with zipfile.ZipFile(par) as archive:
        selected = []
        targets = set()
        for info in archive.infolist():
            safe_member(info.filename)
            if info.is_dir():
                continue
            if stat.S_ISLNK(info.external_attr >> 16):
                raise ValueError(f"Symlink archive member: {info.filename}")
            name = mapped_source(info.filename)
            if name is None:
                continue
            safe_member(name)
            if name in targets:
                raise ValueError(f"Duplicate mapped source: {name}")
            targets.add(name)
            selected.append((info, name))
        destination.mkdir(parents=True)
        provenance = []
        for info, name in selected:
            target = destination / name
            if not target.resolve().is_relative_to(destination.resolve()):
                raise ValueError(f"Escaping source path: {name}")
            target.parent.mkdir(parents=True, exist_ok=True)
            payload = archive.read(info)
            target.write_bytes(payload)
            provenance.append({
                "archive_member": info.filename,
                "output": name,
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            })
    return provenance


def unpack_bundle(archive_path, destination, manifest):
    """Copy only the two pinned executables from the verified official zip."""
    with zipfile.ZipFile(archive_path) as archive:
        selected = {}
        for info in archive.infolist():
            member = safe_member(info.filename)
            if stat.S_ISLNK(info.external_attr >> 16):
                raise ValueError(f"Symlink archive member: {info.filename}")
            if info.is_dir() or member.name not in manifest["files"]:
                continue
            if member.name in selected:
                raise ValueError(f"Duplicate executable: {member.name}")
            selected[member.name] = info
        if set(selected) != set(manifest["files"]):
            raise ValueError("Expected ACP frontend and matching harness in archive")
        destination.mkdir()
        for name, info in selected.items():
            target = destination / name
            with archive.open(info) as source, target.open("xb") as output:
                shutil.copyfileobj(source, output)
            verify_file(target, manifest["files"][name])
            target.chmod(0o755)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--archive", type=Path, help="Official downloaded release zip")
    source.add_argument("--original-dir", type=Path, help="Already extracted pinned executables")
    parser.add_argument("--runtime", type=Path, default=PROJECT / "runtime")
    parser.add_argument("--full-qemu-only", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    destination = args.runtime.expanduser().absolute()
    if destination.exists() or destination.is_symlink():
        parser.error("Runtime destination already exists; choose a new versioned directory")
    if not destination.parent.is_dir():
        parser.error("Runtime parent directory must already exist")
    if args.archive:
        verify_file(args.archive, manifest["archive"])
    else:
        for name, expected in manifest["files"].items():
            verify_file(args.original_dir / name, expected)
    # Publish the prepared directory only after every check has passed.
    with tempfile.TemporaryDirectory(prefix=".agy-prepare-", dir=destination.parent) as tmp:
        staging = Path(tmp) / "payload"
        staging.mkdir()
        if args.archive:
            unpack_bundle(args.archive, staging / "original", manifest)
        else:
            (staging / "original").mkdir()
            for name in manifest["files"]:
                shutil.copyfile(args.original_dir / name, staging / "original" / name)
                verify_file(staging / "original" / name, manifest["files"][name])
                (staging / "original" / name).chmod(0o755)
        if not args.full_qemu_only:
            provenance = extract_sources(
                staging / "original" / "agy_acp_server.par",
                staging / "native" / "src",
            )
            (staging / "native" / "source-provenance.json").write_text(
                json.dumps(provenance, indent=2) + "\n"
            )
            print(f"Extracted {len(provenance)} source/resource files unchanged.")
        (staging / "release-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        staging.rename(destination)
    print(f"Prepared {destination}")
    print("Native mode also requires a local virtual environment; see README.md.")


if __name__ == "__main__":
    main()
