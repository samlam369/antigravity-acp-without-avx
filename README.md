# antigravity-acp-without-avx

Purpose: Provide portable execution wrappers for Google's standalone ACP server
on Linux x86-64 CPUs without AVX. Private working draft, created and reviewed
2026-09-22; broader validation and a license selection remain before release.

`bin/agy-acp-qemu` emulates the packaged frontend and matching harness.
`bin/agy-acp-native` runs the extracted frontend on native Python and emulates
only the harness. `AGY_RUNTIME_DIR` selects a prepared runtime directory and
`AGY_QEMU` selects a QEMU executable name or absolute path. Optional
`AGY_ACP_DEFAULT_MODEL` is inherited unchanged.

Prepare official ACP 1.1.1 using `scripts/prepare_runtime.py --archive FILE`.
The script verifies the manifest hashes and refuses existing destinations.
Native mode additionally requires CPython 3.13, a virtual environment at
`runtime/native/venv`, and the pinned packages in `requirements.txt`.

Run local checks with `python3 -m unittest discover -s tests -v`.

This repository owns authored launchers, scripts, pins and engineering notes.
Acquired executables, extracted modules, environments and diagnostics are
excluded from Git. No active service or client configuration points to this
draft. Keep authored work for maintenance; ignored payloads can be rebuilt,
but an active client would require its selected runtime. Deleting this draft
does not change the existing deployment. Git is not an independent backup.
