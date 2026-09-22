# antigravity-acp-without-avx

Run Google's standalone Antigravity ACP server on Linux x86-64 CPUs without
AVX, using QEMU user-mode emulation. This project provides two local execution
paths: full emulation, and a faster startup path with a native Python frontend
and an emulated official harness.

**Status: private working draft.** Tested against `agy_acp_server_1.1.1`.
The launchers and preparation recipe are ready for review. Broader portability
testing and a license choice for this project's original work remain before
public release. Created and last reviewed: 2026-09-22.

## Scope

The target is the official `agy_acp_server.par` distribution in the
[ACP registry](https://raw.githubusercontent.com/agentclientprotocol/registry/main/antigravity-acp/agent.json),
together with its matching `localharness_external`. This is an execution
compatibility wrapper for that server. It preserves the existing ACP stdio
interface and can be selected as an external command by compatible clients.

The wrapper does not implement a new agent or translate the CLI into ACP.
The optimized path runs extracted, unchanged packaged Python sources against
pinned native dependencies; the official harness still runs through QEMU.
Client compatibility needs its own integration test.

## Two paths

| Path | Frontend | Harness | Main tradeoff |
| --- | --- | --- | --- |
| `bin/agy-acp-qemu` | Official packaged frontend under QEMU | Official harness under QEMU | Smaller dependency surface, slower cold startup |
| `bin/agy-acp-native` | Packaged Python sources on native CPython | Official harness under QEMU | Much faster measured startup, pinned dependency maintenance |

On one Intel Pentium Silver J5005 system, initialization fell from about
**45 seconds to 2.4–3.3 seconds**. With the default model aligned to the
requested model, preparing a session fell from about **61 seconds to 10 seconds**.
These are measured startup results, not a guarantee of response speed on other
machines. See [performance and methodology](docs/performance.md).

## Requirements

- Linux x86-64; the tested CPU has no AVX.
- A QEMU user-mode `qemu-x86_64` executable that can run the pinned binaries.
  The validation used QEMU 10.0.13 with `-cpu max`.
- The official Linux x86-64 ACP 1.1.1 release archive, acquired directly from
  Google. Its URL and locally measured hashes are in
  [the release manifest](manifests/agy-acp-1.1.1-linux-x86_64.json).
- Native mode: CPython 3.13, `venv`, `pip`, and the pinned packages in
  [requirements.txt](requirements.txt). Other Python versions are unverified.
- Several gigabytes of local disk space for the archive, executables and
  native environment. The original frontend alone is about 1.88 GB.

This project does not install system packages, register binary-format handlers,
create a daemon, or edit a client's settings.

## Prepare the runtime

From this checkout, download the official archive:

```sh
mkdir -p artifacts
curl --fail --location \
  'https://dl.google.com/agy-extensions/releases/linux/agy-acp-server-agy_acp_server_1.1.1-linux-x86_64.zip' \
  --output artifacts/agy-acp-server-1.1.1-linux-x86_64.zip

python3 scripts/prepare_runtime.py \
  --archive artifacts/agy-acp-server-1.1.1-linux-x86_64.zip
```

Preparation verifies the pinned archive and executable hashes, creates a new
`runtime/` directory, and extracts the selected Python sources and resources.
It refuses an existing destination. It never executes the downloaded frontend
during extraction. Hashes here were measured locally from the official download;
they are not presented as upstream signed checksums.

For full emulation only, pass `--full-qemu-only`. If you already have the two
official executables, use `--original-dir /path/to/original-files` instead of
`--archive`; both files must match the same pinned release.

For native mode, create its isolated environment:

```sh
python3.13 -m venv runtime/native/venv
runtime/native/venv/bin/python3 -m pip install -r requirements.txt
runtime/native/venv/bin/python3 -m pip check
```

The prepared layout is:

```text
runtime/
├── original/
│   ├── agy_acp_server.par
│   └── localharness_external
├── native/                     # omitted with --full-qemu-only
│   ├── src/
│   ├── source-provenance.json
│   └── venv/                   # created by the venv command
└── release-manifest.json
```

## Configure an ACP client

Use the absolute path to one of these executable commands:

```text
/path/to/antigravity-acp-without-avx/bin/agy-acp-qemu
/path/to/antigravity-acp-without-avx/bin/agy-acp-native
```

The commands communicate using the upstream server's stdio ACP protocol.
Arguments are forwarded. Native mode removes only the packaged launcher's
empty `--uid=` argument because it has no meaning to native Python.
Diagnostics remain on stderr.

Environment options:

| Variable | Default | Purpose |
| --- | --- | --- |
| `AGY_RUNTIME_DIR` | This checkout's `runtime/` | Absolute path to the prepared runtime |
| `AGY_QEMU` | `qemu-x86_64` from `PATH` | Executable name or absolute executable path |
| `AGY_QEMU_CPU` | `max` | QEMU CPU model; alternatives require retesting |
| `AGY_ACP_DEFAULT_MODEL` | Unset | Optional upstream default model, inherited unchanged |

For example, when the client will select this model:

```sh
export AGY_ACP_DEFAULT_MODEL=gemini-3.8-flash-high
/path/to/antigravity-acp-without-avx/bin/agy-acp-native --uid=
```

Setting the desired initial model can avoid starting the harness twice.
The wrapper does not impose a model choice. Model availability and entitlements
remain those of the upstream service.

Keep the checkout and selected runtime at stable paths while configured in a
client. To disable this wrapper, change that client's command back to its
previous value. Nothing runs in the background merely because this repo exists.

## Validation and reading

Run the local preparation/launcher checks with:

```sh
python3 -m unittest discover -s tests -v
```

- [Architecture](docs/architecture.md): what runs natively and what is emulated.
- [Performance](docs/performance.md): startup measurements and rejected shortcuts.
- [Validation](docs/validation.md): direct ACP lifecycle evidence and remaining gaps.
- [Maintenance](docs/maintenance.md): pinned release, rebuild, upgrades and rollback.
- [Troubleshooting](docs/troubleshooting.md): CPU flags, startup and dependency issues.
- [Research and framing](docs/research.md): sources, terminology and project direction.
- [Licensing boundaries](LICENSE-NOTICE.md): original work and acquired components.

## Repository ownership and retention

This repository is the authoritative source for these general launchers,
preparation scripts, dependency pins and engineering notes. It is separate
from any existing machine-specific deployment, and creating this draft changed
no live client configuration.

Downloaded executables, extracted source, virtual environments, diagnostic
artifacts and local configuration are excluded from Git. Keep the authored
files and history for maintenance. Rebuild ignored runtime files from the
pinned sources; validate before removing an active runtime. Removing this
checkout breaks only clients subsequently configured to call its launchers.
Git history alone is not an independent backup.
