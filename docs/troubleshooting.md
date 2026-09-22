# Troubleshooting

## CPU-feature failure or illegal instruction

Read the error from the actual failing executable. `SIGILL`, exit status 132
and a missing CPU-feature message are symptoms; they do not alone identify the
required feature or prove that a particular wrapper will fix it.

Inspect CPU features visible inside the environment:

```sh
grep -m1 '^flags' /proc/cpuinfo
qemu-x86_64 --version
qemu-x86_64 -cpu help
```

A CPU may physically lack AVX, or a virtual-machine CPU model may hide a feature
present on the host. The latter can sometimes be resolved at the virtualization
layer. A Linux container uses the host kernel; changing its configuration does
not add instructions to the physical processor.

This project's tested path emulates the official harness with `-cpu max`.
It does not disable a startup check. An error from the IDE's language server
or the standalone `agy` CLI concerns a different executable; verify the scope
before applying this recipe.

## Error evidence and provenance

The [README error guide](../README.md#startup-errors-and-what-they-mean)
separates reproduced failures, source-defined messages and client summaries.
The evidence was reviewed on 2026-09-22:

- **Packaged frontend:** retained native-start stderr from the official Linux
  x86-64 ACP 1.1.1 `agy_acp_server.par` contains the complete AVX fail-fast
  diagnostic quoted in the README. The tested Intel Pentium Silver J5005 has
  no AVX flag. The exact payload hashes and download URL are in the
  [release manifest](../manifests/agy-acp-1.1.1-linux-x86_64.json).
- **Matching harness:** a native `localharness_external --help` probe returned
  `-4` with empty stdout/stderr. Under QEMU it reached its usage output instead.
  On POSIX, [Python records signal termination as a negative return code](https://docs.python.org/3/library/subprocess.html#subprocess.Popen.returncode);
  here `-4` represents `SIGILL`. An x86-64 Linux shell can instead report status
  132 (128 + signal 4). No individual harness instruction was identified;
  an empty stderr must not be described as a second captured AVX diagnostic.
- **Bundled SDK source:** the four README harness-error prefixes occur in
  `google/antigravity/connections/local/local_connection.py` extracted from
  that pinned PAR. In this version, the relevant lines are 1243 (initial
  handshake), 1196 (WebSocket connection), 1290 (conversation initialization)
  and 533 (unexpected WebSocket closure). These are possible error paths,
  not four independently reproduced AVX failures. Dynamic addresses, close
  codes and stderr are deliberately omitted from the listed prefixes.
- **Client summary:** the downloaded-runtime message was verified in a
  consuming client's installation-verification error handler. It wraps a
  failed check and is not an upstream server diagnostic.
- **Related public evidence:** [SDK issue 147](https://github.com/google-antigravity/antigravity-sdk-python/issues/147)
  reports the AVX fail-fast message in SDK 0.1.7. This corroborates the symptom
  in a related component; it does not establish standalone ACP build flags,
  the precise harness instruction, or compatibility of other releases.

To investigate a matching report, retain the exact command, release/hash,
platform, visible CPU flags, stderr and exit/signal status. Read a client's
underlying process error rather than relying only on its install-failed banner.
For a handshake or WebSocket error, inspect the harness failure before changing
CPU settings: the same error path can also reflect non-CPU problems. Keep raw
logs private when they contain account information, tokens or project paths.

## Initialization is still slow

Confirm that the client selected `agy-acp-native`, and that
`AGY_RUNTIME_DIR/native/venv/bin/python3` is a native host interpreter.
The hybrid path should emulate the harness, while the Python frontend runs
directly. Every fresh process repeats its imports; filesystem cache alone
does not preserve initialized Python objects.

Measure initialize, authentication, session creation and model selection
separately. Align `AGY_ACP_DEFAULT_MODEL` with the model your client selects
when appropriate. A different selection may intentionally rebuild the harness.

Check CPU quota/throttling and memory pressure in your own environment.
Startup readiness and the first model response are different timings.

## Native imports or session restoration fail

Confirm the exact Python version and locked dependencies. Run:

```sh
runtime/native/venv/bin/python3 -m pip check
```

Check that source extraction completed and that the frontend and harness
hashes match the manifest. Do not copy packaged shared objects or bytecode
into the native environment. Keep protobuf at the tested version unless a
replacement passes initialization, tools and restoration.

## Client cannot parse stdout

Keep launcher diagnostics on stderr. The server's stdout belongs to the ACP
protocol. Do not add status banners or shell startup output to the command.

## Permissions and working directory

Launch as the intended OS user, with that user's normal account state and
project access. Use an absolute `AGY_RUNTIME_DIR`; quote executable paths
containing spaces. Client-specific working-directory and environment choices
remain the client's responsibility.

## Upgrade broke the wrapper

Switch back to the previous command/runtime. Create a new versioned runtime
and follow the upgrade checks in [maintenance.md](maintenance.md), preserving
the failed candidate for diagnosis rather than overwriting the working copy.
