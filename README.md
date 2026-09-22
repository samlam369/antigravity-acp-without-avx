# antigravity-acp-without-avx

## In plain English (ELI5)

You want to use Google's Antigravity coding agent in your editor or coding
app, but its helper program will not start on your Linux machine. One possible
reason: the downloaded program expects **AVX**, a set of instructions your
processor does not understand.

This project offers a way to keep using that machine. **QEMU acts like an
interpreter for the program**, allowing it to run despite the missing CPU
instructions. Interpreting the whole program can be slow, so the faster
approach lets more of it run directly and keeps emulation where it is still
needed.

The target is the **official Antigravity ACP server**: the helper that connects
Antigravity to a compatible coding app. You still obtain that software from
Google. This repo supplies the setup tools and instructions to run it in a
different way; it does not supply its own replacement ACP server build.

It keeps Google's own sign-in and service connection code. As far as we can
tell, running the official ACP server through this compatibility layer does
not itself break Google's terms; see
[our reasoning and its limits](docs/research.md#service-access-assessment).

### This may be useful to you if...

- Antigravity fails to start on an older Linux PC, mini PC, NAS or server,
  with an error mentioning missing AVX or an illegal instruction.
- You already run that official helper through QEMU, but each fresh start
  takes a long time.
- You want to keep using the official Antigravity agent through your coding
  app, and are willing to have a coding agent or technical helper adapt the
  setup to your machine.

See [startup errors and what they mean](#startup-errors-and-what-they-mean)
for exact messages. These are clues, not a diagnosis. The tested setup is
**Linux x86-64**; this is not a general fix for the Antigravity desktop app,
every `agy` CLI failure, or account/model-access problems. Your agent should check which
program is failing and whether the CPU requirement is actually the cause.

On one tested machine, getting ready to accept a prompt improved from roughly
**one minute to ten seconds**. That is startup time, not the time to finish a
coding task, and other machines may differ. See the
[measurements and their limits](docs/performance.md).

### Let your coding agent take it from here

You do not need to choose Python versions or QEMU settings first. Give a coding
agent access to this repository and your target machine, tell it which app you
use and what went wrong, and let it assess the fit before adapting the setup.
There is no universal one-click installer; the tested recipe is a starting
point for that work.

<details>
<summary><strong>Copy a starter prompt for your coding agent</strong></summary>

```text
Please assess and, if suitable, adapt this project to my environment:
https://github.com/samlam369/antigravity-acp-without-avx

Target machine: [hostname, or "this machine"]
Coding app/editor: [name, or "please help me identify it"]
Problem: [paste the error or describe the startup delay]

Read the README, docs/architecture.md, docs/maintenance.md,
docs/validation.md and docs/troubleshooting.md before making changes.

First inspect the target OS, architecture, visible CPU features, any VM or
container boundary, and the executable my app actually launches. Confirm
that this is the official standalone ACP server and that this workaround
fits the failure. Do not assume every startup error or SIGILL means AVX.
Check whether an official native runtime already solves the problem.
If the documented platform or release differs, explain and validate the
adaptation rather than applying the recipe blindly.

If appropriate, prepare a separate candidate runtime using the pinned
release, verified hashes, matching frontend/harness and dependency pins.
Choose full QEMU or hybrid execution based on my environment and explain
that choice. Use stable installation paths and my app's supported command
and environment settings; preserve the current setup and a rollback path.

Validate startup, authentication, a model response, tool permissions,
bounded file operations, session restoration, independent concurrent
sessions, cancellation and child-process cleanup. Measure startup readiness
separately from time to first response. Switch the app only after the
candidate passes the relevant checks, then verify the app integration.

Finish with a short explanation of what changed, the measured result,
remaining limitations, how to roll back, and what needs rechecking after
updates. Ask me for missing access or environment details when needed.
```

</details>

Prefer to work through it yourself? Continue with the
[technical scope](#scope) and [requirements](#requirements), then
[prepare the runtime](#prepare-the-runtime).

## Startup errors and what they mean

If you found this project by searching an Antigravity error, compare the
message **and the executable that produced it**. The examples below distinguish
an observed CPU-feature failure from more general symptoms.

### Confirmed AVX startup failure

The official Linux x86-64 `agy_acp_server.par` from release **1.1.1** produced
this exact message on our tested non-AVX machine:

```text
FATAL ERROR: This binary was compiled with avx enabled, but this feature is not available on this processor (go/sigill-fail-fast).
```

This is the failure the tested compatibility path addresses. The matching
`localharness_external` also terminated with **SIGILL** when run natively;
that probe captured no stderr, so it did not identify the particular failing
instruction. See [the evidence and its limits](docs/troubleshooting.md#error-evidence-and-provenance).
A [related upstream SDK report](https://github.com/google-antigravity/antigravity-sdk-python/issues/147)
contains the same AVX diagnostic, but concerns an SDK wheel, not this exact
standalone ACP release.

### Other ways the failure may appear

A shell or process supervisor may report **`SIGILL`**, **`Illegal instruction`**,
**`Illegal instruction (core dumped)`**, or **exit status 132**. Our Python
probe recorded return code **`-4`** for the harness. These are ways to report
an illegal-instruction signal on Linux x86-64, not proof that AVX is the cause;
the exact wording depends on the caller.

The Python SDK code bundled inside the official ACP 1.1.1 release also
contains these error prefixes. They are **source-confirmed possibilities**,
not additional failures reproduced in our AVX test:

| Searchable message prefix | What it tells you |
| --- | --- |
| `Failed to read length from stdout. Stderr:` | The harness supplied no initial handshake header. Check its stderr and termination signal. |
| `Failed to connect to WebSocket at` | The frontend could not establish its local connection to the harness. Inspect the appended endpoint, retry count and stderr. |
| `Failed to initialize conversation at` | Conversation initialization failed over that local connection; inspect the underlying exception and stderr. |
| `Harness process exited unexpectedly (WS close code` | The frontend saw an unexpected WebSocket closure. The message alone does not establish why the harness stopped or disconnected. |

A consuming app may instead show this generic installation/check error:

```text
The downloaded Antigravity runtime could not start in this environment.
```

That message comes from the **client**, not the official ACP server's stderr.
It does not identify a CPU requirement. Obtain the underlying runtime error
before choosing this workaround.

For any generic symptom above, first check the actual executable, release,
CPU features and stderr using the [troubleshooting guide](docs/troubleshooting.md).
Missing files, permissions, local networking and other crashes can produce
similar failures. Errors from the desktop IDE or `agy` CLI concern different
executables; this recipe does not establish compatibility for those products.
You can give the error and this repo to your agent using the
[starter prompt above](#let-your-coding-agent-take-it-from-here).

## Technical overview

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

> [!NOTE]
> This layer adapts local execution of the official ACP implementation, retaining
> upstream authentication and service-access code. It adds no separate login flow,
> service proxy, or mechanism to bypass account entitlements or quotas.
> Based on the implementation and upstream documentation reviewed on 2026-09-23,
> we have not identified a specific basis for concluding that these local
> compatibility adaptations alone introduce a Terms of Service violation.
> This is our assessment, not an explicit Google approval of QEMU or hybrid mode;
> it does not extend to arbitrary clients or uses of the service. See the
> [assessment and sources](docs/research.md#service-access-assessment) and
> [licensing boundaries](LICENSE-NOTICE.md).

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
