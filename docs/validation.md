# Validation record

## Dependency security update on 2026-10-07

The requirements now pin oauthlib 4.0.0 and PyJWT 2.15.0, preserving every
other version including protobuf 6.33.6. Python 3.13 dependency resolution
passed with all 57 packages. The complete list was freshly installed and
validated in a separate native frontend environment on the documented J5005
setup with the official ACP/harness 1.1.1 pair.

These tests passed `pip check`, existing-account authentication,
model replies, exact-command scratch-file write/read/delete, fresh-process
session restoration, two independent concurrent sessions, streaming and
running-tool cancellation, recovery and observed child cleanup. T3 Code
0.0.45 reported the new provider ready/authenticated and passed parallel
diagnostic replies and cancellation/recovery without a service restart.
Synthetic security checks covered both PyJWT advisories, JSONP removal and
constant-time PKCE comparisons. OAuth client PKCE/token exchange/refresh was
also checked with mocked token responses. Fresh interactive login and a
forced real Google token refresh were not tested.

Later on 2026-10-07, a tester reported a successful manual T3 sign-out/sign-in.
The test deployment then passed natural Gemini 3.8 Flash High coding
tasks through T3: file search/read/edit, shell commands, one-time permissions,
bug fixing, seven passing tests, CSV/JSON reports and Git review. Stopping and
resuming the same thread preserved tool operation, and cancellation of an
observed running shell child cleaned it up and allowed a subsequent read.
These additional checks did not exercise browser/MCP tools or force a real
Google token refresh.

All eight preparation/launcher tests in this repository passed. The functional
results were obtained using a separately configured native frontend; the
portable launcher was not separately exercised with a newly prepared runtime
in this checkout. Historical timings below are not measurements of the new
pins, and this update does not patch dependencies embedded in full-QEMU mode.

## Historical validation

The optimized execution boundary was tested directly through ACP on the
pinned Linux x86-64 setup described in [performance.md](performance.md).

| Direct ACP exercise | Observed result |
| --- | --- |
| Fresh initialize and model enumeration | Passed |
| Existing account authentication and model response | Passed |
| Exact-command permission request | Passed |
| Read file, count lines and calculate hash | Passed |
| Exclusive temporary-file write, read and deletion | Passed |
| Restore a prior session in a fresh process and continue | Passed after protobuf was pinned to 6.33.6 |
| Two separate ACP processes used concurrently | Both replied with independent sessions |
| Cancel streaming generation | Request completed; later prompt in the same session succeeded |
| Cancel a bounded running child command | Cancellation worked and child absence was checked |
| Continue after cancellation while the other process remains active | Both sessions remained usable |

These are two independently launched ACP processes, not proof of arbitrary
concurrent calls on one shared SDK Agent or one harness. No shared-harness
pool is implemented.

The pre-existing deployment provided this lifecycle evidence. The general
portable launchers in this repository were additionally checked with
initialize-only execution against the same pinned payload, without changing
an active client. Preparation tests check hashes, archive path handling,
duplicate mappings, refusal to overwrite and argument forwarding.

## Portable launcher checks on 2026-09-22

- Native launcher initialize: **3.179 seconds**.
- Full-QEMU launcher initialize: **44.706 seconds**.
- Both reported protocol version 1 and `agy_acp_server_1.1.1`.
- Both pinned executable hashes matched; a new extraction produced 776 files.
- Native execution reused the already validated pinned virtual environment;
  this was **not** a fresh package installation or a clean-machine rebuild.
- Source extraction was isolated and bytecode writes disabled. Processes were
  stopped after initialize; no model prompt or new authentication was requested.
- Eight focused local tests passed, plus Python compilation and shell syntax
  checks. The tests exercise preparation and launcher boundaries, not the
  upstream model service.

The remaining validation scope includes interactive fresh sign-in, browser
workflows, arbitrary external tool integrations, long-running sessions, other
Linux distributions and Python/QEMU versions, and each consuming client's own
process lifecycle. A successful initialize handshake alone is not equivalent
to validating all of those behaviors.

No account state, conversation content or raw execution traces are distributed
with this repository.
