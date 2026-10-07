# antigravity-acp-without-avx

Run Google's **official Antigravity ACP server on Linux x86-64 CPUs without
AVX**, using QEMU. This repo provides setup scripts and launchers. You download
the official server from Google.

ACP (Agent Client Protocol) connects a coding agent to your editor or coding
app. AVX is a set of CPU instructions that some older processors lack. QEMU
emulates the instructions the server needs. The faster **hybrid mode** runs
the Python frontend directly and emulates only its helper, the *harness*.

**Status:** experimental. Tested with official ACP **1.1.1** on an Intel
Pentium Silver J5005. Other machines and releases need testing.

**Start here:** [set it up yourself](docs/setup.md), or
[give it to your coding agent](#let-your-coding-agent-take-it-from-here).

## Is this for your machine?

This may help if the official standalone ACP server fails because your Linux
x86-64 CPU lacks AVX, or if you already use full QEMU and startup is slow.
Check whether a newer official release already works on your CPU first.

The target is `agy_acp_server.par` and its matching `localharness_external`.
The Antigravity desktop app, `agy` CLI and account-access problems need their
own diagnosis.

### Startup errors and what they mean

On our tested machine, the official ACP 1.1.1 frontend failed with:

```text
FATAL ERROR: This binary was compiled with avx enabled, but this feature is not available on this processor (go/sigill-fail-fast).
```

`SIGILL`, `Illegal instruction` or exit status `132` can also signal a CPU
instruction problem, but do not prove AVX is the cause. Check the failing
executable and its stderr. The [troubleshooting guide](docs/troubleshooting.md)
lists other startup messages, their meaning and the evidence behind them.

## Get started

For manual setup, follow the [setup guide](docs/setup.md). You need QEMU,
several GB of disk space and, for hybrid mode, CPython 3.13. The guide covers
the download, runtime preparation and your client's launch command.

### Let your coding agent take it from here

Give your agent access to this repo and the target machine. There is no
one-click installer; the tested recipe may need adapting to your environment.

<details>
<summary><strong>Copy a starter prompt</strong></summary>

```text
Help me use https://github.com/samlam369/antigravity-acp-without-avx

Target machine: [hostname, or "this machine"]
Coding app/editor: [name]
Problem: [error or startup delay]

Read the README and the setup, architecture, troubleshooting, maintenance
and validation guides in docs/.

Check the OS, CPU features, VM/container boundaries and the executable my
app launches. Confirm this workaround fits; SIGILL alone does not prove
an AVX problem. Check for a working official native release first.

If suitable, prepare a separate runtime with the verified release,
matching harness and pinned dependencies. Explain the execution mode
you choose. Keep my working setup and a rollback path.

Run the relevant validation checks, including authentication, model
replies, tool permissions, bounded file operations, session restoration,
independent sessions, cancellation and child cleanup. Measure startup
readiness separately from response time. Switch only after these pass,
then check my app integration.

Summarize changes, results, limits, rollback and future update checks.
Ask for missing access or environment details when needed.
```

</details>

## How it works

| Mode | What runs under QEMU | Tradeoff |
| --- | --- | --- |
| Full QEMU: `bin/agy-acp-qemu` | Official packaged frontend and harness | Fewer separate dependencies; slower startup |
| Hybrid: `bin/agy-acp-native` | Official harness only; extracted Python frontend runs natively | Faster measured startup; native dependencies need maintenance |

On the tested J5005, initialization fell from about **45 seconds to 2.4–3.3
seconds**. Prompt readiness fell from about **61 seconds to 10 seconds**;
that comparison also aligned the default model to avoid a second harness
start. These are startup timings on one machine, not coding-task response
times. See [measurements and limits](docs/performance.md).

## Compatibility and terms

This is an unofficial way to run the official server. Hybrid mode keeps the
extracted source files and matching harness unchanged, but changes Python,
packaging and dependencies. Each client and runtime update needs testing.
See [architecture](docs/architecture.md) and [dependency versions](docs/maintenance.md).

Google's authentication and service-access code remain in use. Based on the
implementation and upstream documents reviewed, we found no specific basis
for concluding that these local changes alone violate Google's terms. This
is our assessment, not Google approval; see its
[scope and limits](docs/research.md#service-access-assessment).

Original scripts and documentation are licensed under [MIT](LICENSE).
Third-party components retain their own licenses.
See [component notices](LICENSE-NOTICE.md).

## Documentation

| What you need | Guide |
| --- | --- |
| Install and configure a client | [Setup](docs/setup.md) |
| Diagnose a startup error | [Troubleshooting](docs/troubleshooting.md) |
| Understand what runs where | [Architecture](docs/architecture.md) |
| Check the speed measurements | [Performance](docs/performance.md) |
| See what was tested | [Validation](docs/validation.md) |
| Rebuild, upgrade or roll back | [Maintenance](docs/maintenance.md) |
| Compare approaches and check sources | [Background and sources](docs/research.md) |
