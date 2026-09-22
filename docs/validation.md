# Validation record

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
