# Architecture

## Execution boundary

Full user-mode emulation:

```text
ACP client
  -> agy-acp-qemu
     -> qemu-x86_64 -> official packaged Python frontend
        -> localharness-qemu
           -> qemu-x86_64 -> official localharness_external
```

Native frontend:

```text
ACP client
  -> agy-acp-native
     -> native CPython + extracted packaged frontend/SDK sources
        -> localharness-qemu
           -> qemu-x86_64 -> official localharness_external
```

QEMU user-mode translates application instructions and interfaces with the
host kernel. There is no guest firmware, guest operating-system boot, virtual
disk or VM service in either path.
[QEMU user-mode documentation](https://www.qemu.org/docs/master/user/main.html)

The CPU still lacks AVX. Emulation supplies the execution capability required
by the proprietary harness. Removing a feature check would not implement the
missing instructions.

## What the native path changes

The pinned PAR is also readable as a ZIP archive. The preparation script
copies selected `.py` files and resources, preserving each file's bytes.
It maps the packaged `google/antigravity` and `acp` modules to native import
paths. Packaged shared objects, Python bytecode and the hermetic Python
interpreter are not reused.

A dedicated native Python virtual environment supplies public dependencies.
The bootstrap applies the protobuf version-validation shim already present in
the official entrypoint before generated internal modules are imported. It
also filters the exact empty `--uid=` launcher argument. It does not rewrite
the packaged session, permission or model-selection implementations.

The wrapper selects the harness through `ANTIGRAVITY_HARNESS_PATH`. The helper
executes the matching original harness through QEMU. Launchers use `exec`,
preserving the process-facing stdio and termination behavior as far as the
underlying programs permit. There is one ordinary launch per client process;
no pool, broker or cross-session harness sharing is introduced.

## Why startup improves

Importing Python modules executes code: classes, data schemas and runtime
objects are built again in every fresh process. Running this work on native
CPython removes most of the frontend's emulation overhead. It does not make
the remaining harness native or remove model-service waiting.

The upstream default-model setting is a separate optimization. If a client
creates a session using the server default and then selects a different model,
the pinned implementation replaces its agent/harness. Aligning the initial
default with the intended selection avoids that second startup.

## Compatibility surface

The upstream ACP server and its matching harness remain version 1.1.1.
The executable packaging and frontend dependency environment change. Matching
the version is necessary but does not guarantee every behavior is identical.

The boundary exposed to clients is standard ACP over stdio, not a
client-specific internal API. A client upgrade can still change arguments,
environment, protocol expectations or process lifecycle; perform a smoke test
after upgrading a client. An upstream ACP upgrade requires a deliberate
payload/dependency refresh and broader tests.
