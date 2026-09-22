# antigravity-acp-without-avx

A practical **compatibility and startup optimization strategy, with reference
tooling**, for running Google's **official standalone Antigravity ACP server**
on tested Linux x86-64 CPUs without AVX.

This repository documents a working approach and provides launchers, pinned
setup tooling and engineering evidence. **It does not provide a third-party
ACP server build:** it neither implements a separate ACP server nor distributes
a prebuilt Antigravity runtime. Users obtain the official release from Google
and use these tools to prepare and run it locally.

**Status: private working draft.** Tested against `agy_acp_server_1.1.1`.
The launchers and preparation recipe are ready for review. Broader portability
testing and a license choice for this project's original work remain before
public release. Created and last reviewed: 2026-09-22.

## Scope

The target is the official `agy_acp_server.par` distribution in the
[ACP registry](https://raw.githubusercontent.com/agentclientprotocol/registry/main/antigravity-acp/agent.json),
together with its matching `localharness_external`. The compatibility layer
reuses that server's ACP implementation and exposes its existing stdio
interface to compatible clients. It does not introduce its own agent harness
or translate the `agy` CLI into ACP.

Two reference execution paths demonstrate the strategy: full QEMU emulation,
and **hybrid execution (native Python frontend + QEMU-emulated harness)**.
The hybrid path runs extracted, unchanged packaged Python sources against
pinned native dependencies while keeping the matching official harness
binary unchanged under QEMU.

The hybrid path changes packaging and the frontend execution environment; it
is more than a thin shell wrapper. Dependency compatibility and lifecycle
behavior require maintenance and testing. It is an unofficial adaptation,
not a Google-supported runtime build or a guarantee that every behavior is
identical to the original packaged environment. Each client needs its own
integration test.

## Two reference execution paths

| Path | Frontend | Harness | Main tradeoff |
| --- | --- | --- | --- |
| `bin/agy-acp-qemu` | Official packaged frontend under QEMU | Official harness under QEMU | Smaller dependency surface, slower cold startup |
| `bin/agy-acp-native` | Packaged Python sources on native CPython | Official harness under QEMU | Much faster measured startup, pinned dependency maintenance |

On one Intel Pentium Silver J5005 system, initialization fell from about
**45 seconds to 2.4–3.3 seconds**. With the default model aligned to the
requested model, preparing a session fell from about **61 seconds to 10 seconds**.
These are measured startup results, not a guarantee of response speed on other
machines. See [performance and methodology](docs/performance.md).

## How this differs from other ACP projects

| Approach | What it supplies | What still needs to work locally |
| --- | --- | --- |
| This compatibility layer | Launchers and preparation tooling around the official ACP implementation | The pinned upstream payload, native dependencies where used, and QEMU |
| CLI-to-ACP adapter | Its own ACP implementation translating to and from a CLI | The CLI and its downstream runtime dependencies |
| SDK-based ACP frontend | Its own ACP implementation and agent configuration on top of an SDK | The SDK and any native harness it launches |

A different ACP frontend does not by itself remove a native executable's CPU
requirements. Conversely, a newer CLI or SDK might have different hardware
compatibility from the pinned standalone release here; assess that exact
version rather than assuming either success or failure. Permissions, session
restoration, cancellation, prompting and time to first useful response also
need comparison. See [project positioning](docs/research.md).

## When this approach is useful

Use this approach when retaining the official standalone ACP implementation
matters, its packaged runtime does not run on the target CPU, and the tested
compatibility path meets your needs. The reference tooling makes the approach
reproducible; its scope remains the pinned configuration and documented tests.

The workaround can be retired when an official native release works on the
target hardware, or a tested alternative better meets the required behavior
and performance. Keep the old environment until the replacement passes
permissions, tools, session restoration, cancellation and concurrency checks.
There is no need to grow this project into another ACP server implementation.

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
