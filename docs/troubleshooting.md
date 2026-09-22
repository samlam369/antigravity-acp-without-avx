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
