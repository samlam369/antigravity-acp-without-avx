"""Local checks for preparation safety and wrapper command boundaries."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import zipfile

PROJECT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "prepare_runtime", PROJECT / "scripts" / "prepare_runtime.py"
)
prepare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare)


class PreparationTests(unittest.TestCase):
    def test_hash_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input"
            path.write_bytes(b"payload")
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                prepare.verify_file(path, {"sha256": "0" * 64})
            prepare.verify_file(path, {
                "sha256": hashlib.sha256(b"payload").hexdigest(), "bytes": 7
            })

    def test_escaping_paths_are_rejected(self):
        for name in ("../escape", "/absolute", "a/../../escape", "a\\escape", "C:/escape"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                prepare.safe_member(name)

    def test_source_selection_and_byte_preservation(self):
        with tempfile.TemporaryDirectory() as tmp:
            par, target = Path(tmp) / "input.par", Path(tmp) / "src"
            with zipfile.ZipFile(par, "w") as archive:
                archive.writestr("google3/third_party/py/acp/schema.py", b"VALUE=42\n")
                archive.writestr("google3/internal/module.py", b"VALUE=43\n")
                archive.writestr("google3/third_party/py/other/module.py", b"omit")
                archive.writestr("binary.so", b"omit")
            provenance = prepare.extract_sources(par, target)
            self.assertEqual((target / "acp/schema.py").read_bytes(), b"VALUE=42\n")
            self.assertEqual(len(provenance), 2)
            self.assertFalse((target / "binary.so").exists())
            with self.assertRaises(FileExistsError):
                prepare.extract_sources(par, target)

    def test_path_traversal_fails_before_destination_created(self):
        with tempfile.TemporaryDirectory() as tmp:
            par, target = Path(tmp) / "input.par", Path(tmp) / "src"
            with zipfile.ZipFile(par, "w") as archive:
                archive.writestr("../outside.py", "bad")
            with self.assertRaises(ValueError):
                prepare.extract_sources(par, target)
            self.assertFalse(target.exists())

    def test_mapped_duplicate_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            par, target = Path(tmp) / "input.par", Path(tmp) / "src"
            with zipfile.ZipFile(par, "w") as archive:
                archive.writestr("google3/third_party/py/acp/schema.py", "one")
                archive.writestr("acp/schema.py", "two")
            with self.assertRaisesRegex(ValueError, "Duplicate mapped"):
                prepare.extract_sources(par, target)

    def test_cli_refuses_existing_runtime_before_input_access(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run([
                "python3", str(PROJECT / "scripts/prepare_runtime.py"),
                "--original-dir", str(Path(tmp) / "absent"),
                "--runtime", tmp,
            ], text=True, capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("already exists", result.stderr)


class LauncherTests(unittest.TestCase):
    def test_space_paths_arguments_and_optional_model_are_preserved(self):
        with tempfile.TemporaryDirectory(prefix="agy test ") as tmp:
            root = Path(tmp)
            runtime = root / "runtime dir"
            runtime.mkdir()
            qemu = root / "fake qemu"
            qemu.write_text(
                "#!/usr/bin/env python3\n"
                "import json,os,sys\n"
                "print(json.dumps({'argv':sys.argv[1:],"
                "'runtime':os.environ.get('AGY_RUNTIME_DIR'),"
                "'model':os.environ.get('AGY_ACP_DEFAULT_MODEL')}))\n"
            )
            qemu.chmod(0o755)
            env = dict(os.environ, AGY_RUNTIME_DIR=str(runtime), AGY_QEMU=str(qemu))
            for model in (None, "example-model"):
                env.pop("AGY_ACP_DEFAULT_MODEL", None)
                if model is not None:
                    env["AGY_ACP_DEFAULT_MODEL"] = model
                for launcher, target in (
                    ("agy-acp-qemu", "agy_acp_server.par"),
                    ("localharness-qemu", "localharness_external"),
                ):
                    result = subprocess.run([
                        str(PROJECT / "bin" / launcher), "--uid=", "literal space"
                    ], env=env, text=True, capture_output=True, check=True)
                    record = json.loads(result.stdout)
                    self.assertEqual(record["argv"], [
                        "-cpu", "max", str(runtime / "original" / target),
                        "--uid=", "literal space",
                    ])
                    self.assertEqual(record["model"], model)

    def test_relative_qemu_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [str(PROJECT / "bin/agy-acp-qemu")],
                env=dict(os.environ, AGY_RUNTIME_DIR=tmp, AGY_QEMU="./qemu"),
                text=True, capture_output=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("absolute path", result.stderr)


if __name__ == "__main__":
    unittest.main()
