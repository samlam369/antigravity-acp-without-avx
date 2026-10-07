# Architecture

This project runs Google's official standalone Antigravity ACP server on
tested Linux x86-64 hardware without AVX. Its tools prepare a local runtime
from files you download from Google. It does not provide a replacement ACP
server or a prebuilt runtime.

The server has two parts: a Python frontend that talks to the ACP client,
and the `localharness_external` executable that runs the agent. In the pinned
1.1.1 source, the frontend creates the packaged Python SDK Agent, which
launches the harness directly. This path does not first run the `agy` CLI.

## Execution boundary

Full QEMU mode runs both parts under emulation:

```text
ACP client
  -> agy-acp-qemu
     -> qemu-x86_64 -> official packaged Python frontend
        -> localharness-qemu
           -> qemu-x86_64 -> official localharness_external
```

Hybrid mode runs the Python frontend directly on the host. Only the harness
uses QEMU:

```text
ACP client
  -> agy-acp-native
     -> native CPython + extracted packaged frontend/SDK sources
        -> localharness-qemu
           -> qemu-x86_64 -> official localharness_external
```

[QEMU user-mode](https://www.qemu.org/docs/master/user/main.html) translates
the program's instructions and uses the host kernel. Neither path boots a
guest operating system or needs guest firmware, a virtual disk or a VM service.
The CPU still lacks AVX; QEMU emulates the instructions the harness needs.
Removing a CPU feature check would not supply those instructions.

## What the native path changes

The pinned `agy_acp_server.par` can also be read as a ZIP archive. The
preparation script copies selected `.py` files and resources without changing
their bytes. It puts the copied `google/antigravity` and `acp` modules on paths
native Python can import. It does not reuse the packaged shared
libraries, Python bytecode or bundled Python interpreter.

A dedicated Python virtual environment supplies the public dependencies.
Before loading generated internal modules, the bootstrap applies the same
protobuf version-check override as the official entrypoint. It also removes
the exact empty launcher argument `--uid=`. The packaged session, permission
and model-selection code stays unchanged.

The wrapper sets `ANTIGRAVITY_HARNESS_PATH` to `localharness-qemu`, which runs
the matching original harness through QEMU. The launchers use `exec` to keep
stdio and termination behavior as close to the underlying programs as possible.
Each client process gets its own launch. There is no process pool, broker or
shared harness across sessions.

## Why startup improves

Every fresh Python process builds classes, data schemas and other objects
when it imports modules. Native CPython does this work without QEMU's
emulation overhead. The harness still needs emulation, and requests still
wait for the model service.

The upstream default-model setting saves another startup. In the pinned
release, creating a session with the default model and then selecting a
different model replaces the agent and harness. Setting the initial default
to the intended model avoids that second launch.

## Compatibility surface

The official ACP server and harness remain version 1.1.1. Hybrid mode changes
how the frontend is packaged and which dependencies it uses. Keeping the
server and harness versions matched does not guarantee identical behavior.

Clients use standard ACP over stdio. A client update can change arguments,
environment variables, protocol expectations or how processes start and stop.
Run an integration smoke test after updating a client. For an official ACP
upgrade, refresh the matching files and dependencies, then run the broader
checks in [maintenance and upgrades](maintenance.md).
