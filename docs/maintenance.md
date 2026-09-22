# Maintenance and upgrades

## Pin the complete execution boundary

Track the official archive version and SHA-256, the frontend and harness hashes,
QEMU version/CPU model, native Python version, complete Python dependency list,
and the extraction/bootstrap code together. The release manifest records
locally measured hashes rather than implying an upstream signature.

The frontend sources and harness must come from the same official release.
Do not install an arbitrary newest public SDK alongside an older harness.
The public SDK package and extracted packaged modules are not interchangeable
merely because their import names overlap.

The current dependency pin uses protobuf 6.33.6. An exploratory run with
7.36.2 initialized successfully but failed session restoration because the
packaged loader uses the removed `FieldDescriptor.label` API. This is why
testing only `initialize` is insufficient.

## Reproduce a runtime

1. Obtain the official archive named by the manifest.
2. Run the preparation script into a new directory; do not edit an active runtime.
3. Create the native virtual environment with the tested Python version.
4. Install `requirements.txt` and run `python -m pip check`.
5. Compare the generated source provenance and expected extraction count
   (776 files for this pin).
6. Run initialization, authentication, tool permission/read/write, resume,
   concurrent-process and cancellation checks.
7. Point a test client at the new runtime using `AGY_RUNTIME_DIR`.
8. Switch a live client only after its own integration smoke test.

Package versions are fixed, but this draft is not a wheelhouse with artifact
hashes. Rebuilding still depends on package availability and compatible native
wheels. Preserve the currently working runtime until its replacement passes.

## Changes by layer

| Changed layer | Required maintenance |
| --- | --- |
| ACP client only | Check launch configuration, arguments, protocol compatibility, new session, resume and cancellation |
| Official ACP or harness | Refresh matching payload, verify source layout, re-evaluate bootstrap/dependencies, repeat lifecycle checks |
| Python/dependencies | Rebuild in a new environment; include session restoration and native extension import checks |
| QEMU/kernel/container environment | Recheck instructions, startup, tools, subprocess cancellation and cleanup |
| Default model | Verify model availability and whether the selected model avoids a second harness start |

An unchanged ACP version reduces one source of change. It does not make future
client updates automatically safe.

## Rollback and removal

Keep the previous runtime and client command until the new path is established.
Rollback means restoring that command and runtime selection, then letting the
client start a fresh process. Existing session compatibility remains the
upstream server's responsibility; do not assume a newer server's saved state
is always backward compatible.

No system service is installed by this repository. Remove a client reference
before moving the checkout or deleting its selected runtime. Generated payloads
are ignored by Git but required while a client uses them.

## Public-release checklist

Choose a license for original work; review component notices and references;
rebuild from the documented recipe; review tracked content for machine-specific
configuration; verify the compatibility matrix; keep the release experimental
until independent installations are tested. A public repository should contain
authored code and reproducible acquisition instructions, not acquired runtime
payloads.
