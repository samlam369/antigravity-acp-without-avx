# Maintenance and upgrades

Build each replacement in a new directory. Keep the working runtime and client
command until the replacement passes validation. For the commands, use the
[setup guide](setup.md).

## Pin the complete execution boundary

Record these together: official archive version and SHA-256, frontend and
harness hashes, QEMU version and CPU model, native Python version, all Python
dependency versions, and the extraction/bootstrap code. The release manifest
contains locally measured hashes, not an upstream signature.

The frontend sources and harness must come from the same official release.
Do not pair an older harness with the latest public SDK. The public SDK and
extracted modules can share import names without being interchangeable.

Keep protobuf at 6.33.6 for this release. A trial with 7.36.2 passed
`initialize` but could not restore a session: the packaged loader uses
`FieldDescriptor.label`, which that version no longer provides. Always test session
restoration as well as initialization.

## Native dependency updates

Hybrid mode installs public packages from [requirements.txt](../requirements.txt).
Two current pins are newer than the versions declared by bundled source in
the official Linux x86-64 `agy_acp_server_1.1.1` PAR:

| Library | Version declared by bundled source | Native frontend pin |
| --- | --- | --- |
| oauthlib | 2.0.7 | 4.0.0 |
| PyJWT (`jwt`) | 2.13.0 | 2.15.0 |

The bundled versions were read from `__version__` fields under
`google3/third_party/py/` on 2026-10-07. These identify the bundled source;
they do not prove it is equivalent to public packages with the same numbers.

The 2026-10-07 update addressed GHSA-hj66-6f7g-4r5v, GHSA-xpv3-w29h-x7cv,
GHSA-42vr-xj54-vc7v and GHSA-x33g-cr3x-6449. All other pins stayed the same.
Validation used all 57 packages in a fresh Python 3.13.5 venv with a separately
configured native frontend and the official ACP/harness 1.1.1 pair. It covered
model replies, session restoration, independent concurrent sessions, bounded
file operations, cancellation/recovery and T3 Code 0.0.45 integration. See
[the validation scope](validation.md#dependency-security-update-on-2026-10-07).

Rebuild existing native venvs to apply these fixes. Changing the pins in the
repo does not update an installed environment. Google's frontend OAuth code
and matching harness stay unchanged. The original PAR, including full-QEMU
mode, keeps its bundled libraries; these pins do not patch them.

## Reproduce a runtime

1. Obtain the official archive named by the manifest.
2. Run the preparation script into a new directory.
3. Create the native virtual environment with the tested Python version.
4. Install `requirements.txt` and run `python -m pip check`.
5. Compare the source hashes in `source-provenance.json` and check the
   extraction count (776 files for this pin).
6. Run initialization, authentication, tool permission/read/write, resume,
   concurrent-process and cancellation checks.
7. Point a test client at the new runtime using `AGY_RUNTIME_DIR`.
8. Switch a live client only after its own integration smoke test.

Full-QEMU mode does not need the native environment or extraction checks in
steps 3–5.

Package versions are pinned, but the repo does not include an archive of
package downloads or their hashes. Rebuilding depends on those packages and
compatible native wheels remaining available.

## Changes by layer

| Changed layer | Required maintenance |
| --- | --- |
| ACP client only | Check launch configuration, arguments, protocol compatibility, new session, resume and cancellation |
| Official ACP or harness | Refresh matching payload, verify source layout, re-evaluate bootstrap/dependencies, repeat lifecycle checks |
| Python/dependencies | Rebuild in a new environment; include session restoration and native extension import checks |
| QEMU/kernel/container environment | Recheck instructions, startup, tools, subprocess cancellation and cleanup |
| Default model | Verify model availability and whether the selected model avoids a second harness start |

## Rollback and removal

To roll back, restore the previous client command and runtime selection, then
let the client start a fresh process. The upstream server controls saved-session
compatibility. An older server may not be able to read a newer server's saved
state.

The repo installs no system service. Remove the client's reference before
moving the checkout or deleting its runtime. Git ignores generated runtime
files, but the client still needs them.

## Release checklist

- Choose a license for original work and review component notices and references.
- Rebuild from the documented recipe and verify the compatibility matrix.
- Check tracked files for machine-specific configuration or downloaded runtime files.
- Keep the release experimental until independent installations are tested.

Publish the authored code and instructions for obtaining the runtime files.
Keep acquired runtime files out of the public repository.
