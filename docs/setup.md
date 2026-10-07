# Set up Antigravity ACP without AVX

This recipe prepares official ACP **1.1.1** for Linux x86-64. Start with
[the README](../README.md) to check whether it fits your machine. If you
already have a working setup, keep it while you test a separate runtime.

## Requirements

- Linux x86-64. The tested CPU is an Intel Pentium Silver J5005 without AVX.
- QEMU user-mode with the `qemu-x86_64` executable. Validation used QEMU
  10.0.13 with `-cpu max`.
- Python 3.9 or later to run the preparation script.
- Hybrid mode: CPython 3.13 with `venv` and `pip`. Validation used 3.13.5;
  other Python versions are unverified for the frontend.
- Several GB of free disk space for the archive, executables and native
  environment. The original frontend alone is about 1.88 GB.
- A compatible ACP client and access to Google's Antigravity service.

The scripts prepare files locally. They do not install system packages,
register binary-format handlers, create a daemon or edit your client's settings.

## 1. Choose an execution mode

| Mode | Use it when | Launcher |
| --- | --- | --- |
| Hybrid | You want the faster measured startup and can maintain a native Python environment | `bin/agy-acp-native` |
| Full QEMU | You want to run the original packaged frontend without separate Python dependencies | `bin/agy-acp-qemu` |

Both modes run the official harness under QEMU. Hybrid mode runs the extracted
Python frontend directly with [pinned dependencies](../requirements.txt).
See [what this changes](architecture.md) and [the tested limits](validation.md).

## 2. Download and prepare the official release

Run these commands from this checkout:

```sh
mkdir -p artifacts
curl --fail --location \
  'https://dl.google.com/agy-extensions/releases/linux/agy-acp-server-agy_acp_server_1.1.1-linux-x86_64.zip' \
  --output artifacts/agy-acp-server-1.1.1-linux-x86_64.zip

python3 scripts/prepare_runtime.py \
  --archive artifacts/agy-acp-server-1.1.1-linux-x86_64.zip
```

For full QEMU only, add `--full-qemu-only` to the preparation command. This
skips Python source extraction; you can also skip step 3.

Preparation checks the archive and executable hashes against the
[release manifest](../manifests/agy-acp-1.1.1-linux-x86_64.json). It creates
`runtime/` and refuses to overwrite an existing destination. It does not
execute the downloaded frontend during extraction. These hashes were measured
locally from Google's download; they are not upstream signed checksums.

To prepare another runtime, use `--runtime /absolute/path/to/new-runtime`;
its parent directory must exist. Use that path in later commands and set
`AGY_RUNTIME_DIR` in your client. If you already have both official executables,
use `--original-dir /path/to/original-files` instead of `--archive`. Both files
must match the pinned release.

## 3. Create the hybrid Python environment

```sh
python3.13 -m venv runtime/native/venv
runtime/native/venv/bin/python3 -m pip install -r requirements.txt
runtime/native/venv/bin/python3 -m pip check
```

Use the pins as a set. Some public packages differ from the bundled versions;
see [dependency versions and update checks](maintenance.md#native-dependency-updates).

The prepared layout is:

```text
runtime/
├── original/
│   ├── agy_acp_server.par
│   └── localharness_external
├── native/                     # omitted with --full-qemu-only
│   ├── src/
│   ├── source-provenance.json
│   └── venv/                   # created in step 3
└── release-manifest.json
```

## 4. Configure and test your ACP client

Set a test client's command to the absolute path of your chosen launcher:

```text
/path/to/antigravity-acp-without-avx/bin/agy-acp-native
```

For full QEMU, use `bin/agy-acp-qemu` instead. Follow your client's supported
command and environment settings. The launchers use the upstream server's
stdio ACP protocol and send diagnostics to stderr. Arguments are forwarded;
hybrid mode removes only the packaged launcher's empty `--uid=` argument.

| Environment variable | Default | Purpose |
| --- | --- | --- |
| `AGY_RUNTIME_DIR` | This checkout's `runtime/` | Absolute path to the prepared runtime |
| `AGY_QEMU` | `qemu-x86_64` from `PATH` | Executable name or absolute executable path |
| `AGY_QEMU_CPU` | `max` | QEMU CPU model; retest if you change it |
| `AGY_ACP_DEFAULT_MODEL` | Unset | Optional upstream default model |

Set the initial model to the one your client will select if you want to avoid
a second harness start. For example, if your account and client use this model:

```sh
export AGY_ACP_DEFAULT_MODEL=gemini-3.8-flash-high
/path/to/antigravity-acp-without-avx/bin/agy-acp-native --uid=
```

For a GUI client, put the variable in its launch environment. Model availability
and account entitlements remain those of the upstream service.

Before switching your regular client, check startup, authentication, a model
reply, tool permissions, bounded file operations, session restoration,
independent concurrent sessions, cancellation and child-process cleanup.
Use the [validation record](validation.md) to understand what has already
been tested and what needs checking in your environment.

The repo also has local preparation and launcher tests:

```sh
python3 -m unittest discover -s tests -v
```

These tests do not connect to the model service or validate your app integration.
For errors, use [troubleshooting](troubleshooting.md).

## Keep the setup working

Keep the checkout and selected runtime at stable paths while your client uses
them. To roll back, restore the previous client command and runtime selection,
then start a fresh process. See [maintenance](maintenance.md) before updates.

Downloaded executables, extracted sources, virtual environments and local
configuration are excluded from Git. Keep the authored files and history;
rebuild generated files from the pinned sources. Remove the client reference
before moving or deleting its checkout or runtime. Git history is not an
independent backup.
