# Troubleshooting

Start with the **exact error and the program that produced it**. This guide
covers the official Linux x86-64 ACP server and its matching harness. The
desktop IDE and standalone `agy` CLI use different executables.

## Error evidence and provenance

The evidence below was reviewed on 2026-09-22. It separates captured failures
from possible error messages and generic client summaries.

### Confirmed AVX startup failure

The official ACP 1.1.1 `agy_acp_server.par` produced this exact stderr on an
Intel Pentium Silver J5005 with no AVX flag:

```text
FATAL ERROR: This binary was compiled with avx enabled, but this feature is not available on this processor (go/sigill-fail-fast).
```

This is the failure the tested compatibility path addresses. The
[release manifest](../manifests/agy-acp-1.1.1-linux-x86_64.json) records the
download URL and exact payload hashes.

The matching `localharness_external --help` probe returned `-4` when run
natively, with empty stdout and stderr. Under QEMU it reached its usage output.
On POSIX, [Python uses negative return codes for signal termination](https://docs.python.org/3/library/subprocess.html#subprocess.Popen.returncode):
`-4` means `SIGILL`. No individual harness instruction was identified. This
probe did not capture a second AVX diagnostic.

[SDK issue 147](https://github.com/google-antigravity/antigravity-sdk-python/issues/147)
reports the same AVX message in SDK 0.1.7. It supports the symptom in that
related component. It does not establish the standalone ACP build flags,
the failing harness instruction, or compatibility of other releases.

### Illegal-instruction symptoms

A shell or process supervisor may report `SIGILL`, `Illegal instruction`,
`Illegal instruction (core dumped)`, or exit status 132. On Linux x86-64,
132 is 128 + signal 4. The wording depends on the caller.

These symptoms do not identify the missing CPU feature. Check the failing
executable, visible CPU flags and stderr before choosing a workaround.

### Source-confirmed harness errors

The SDK bundled in official ACP 1.1.1 contains these prefixes. They are
possible error paths, **not four reproduced AVX failures**.

| Searchable message prefix | What to check |
| --- | --- |
| `Failed to read length from stdout. Stderr:` | The harness supplied no initial handshake header. Check its stderr and termination signal. |
| `Failed to connect to WebSocket at` | The frontend could not connect to the harness. Check the appended endpoint, retry count and stderr. |
| `Failed to initialize conversation at` | Conversation initialization failed. Check the underlying exception and stderr. |
| `Harness process exited unexpectedly (WS close code` | The frontend saw an unexpected WebSocket closure. Check why the harness stopped or disconnected. |

The source is `google/antigravity/connections/local/local_connection.py`,
extracted from the pinned PAR. The relevant lines are 1243, 1196, 1290 and
533, respectively. The prefixes omit dynamic addresses, close codes and stderr.
Missing files, permissions, local networking and other crashes can also
trigger these paths.

### Generic client error

A consuming app may show:

```text
The downloaded Antigravity runtime could not start in this environment.
```

This message was verified in a client's installation-check error handler.
It summarizes a failed check; it is not the official server's stderr and does
not identify a CPU requirement. Obtain the underlying process error.

## CPU-feature failure or illegal instruction

Read the error from the actual failing executable. `SIGILL`, exit status 132
and a CPU-feature message do not alone prove that this wrapper applies.

Inspect CPU features visible inside the environment:

```sh
grep -m1 '^flags' /proc/cpuinfo
qemu-x86_64 --version
qemu-x86_64 -cpu help
```

A CPU may lack AVX. A virtual machine may also hide a feature that the host has;
changing the VM's CPU model can sometimes fix that. A Linux container uses the
host kernel. Its configuration cannot add instructions to the physical CPU.

This project's tested path emulates the official harness with `-cpu max`.
It does not disable a startup check.

Keep the exact command, release/hash, platform, visible CPU flags, stderr and
exit/signal status. For handshake or WebSocket errors, inspect the harness
failure before changing CPU settings. Keep logs private if they contain account
information, tokens or project paths.

## Initialization is still slow

Check that the client selected `agy-acp-native`, and that
`AGY_RUNTIME_DIR/native/venv/bin/python3` is a native host interpreter.
In hybrid mode, the Python frontend runs directly and QEMU runs the harness.
Every fresh process repeats its imports. Filesystem cache does not preserve
initialized Python objects.

Measure initialize, authentication, session creation and model selection
separately. Setting `AGY_ACP_DEFAULT_MODEL` to the model your client selects
can avoid a second harness launch.

Check CPU quota/throttling and memory pressure in your own environment.
Startup readiness and the first model response are different timings. See the
[measured results and limits](performance.md).

## Native imports or session restoration fail

Check the Python version and pinned dependencies. From the checkout, run:

```sh
runtime/native/venv/bin/python3 -m pip check
```

Check that source extraction completed and that the frontend and harness
hashes match the manifest. Do not copy packaged shared objects or bytecode
into the native environment. Keep protobuf at the tested version unless a
replacement passes initialization, tools and session restoration.

## Client cannot parse stdout

Keep launcher diagnostics on stderr. The server's stdout belongs to the ACP
protocol. Do not add status banners or shell startup output to the command.

## Permissions and working directory

Launch as the intended OS user, with that user's normal account state and
project access. Use an absolute `AGY_RUNTIME_DIR`; quote executable paths
containing spaces. The client controls its working directory and environment.

## Upgrade broke the wrapper

Switch back to the previous command/runtime. Keep the failed candidate for
diagnosis. Create a new versioned runtime and follow the
[upgrade checks](maintenance.md) without overwriting the working copy.
