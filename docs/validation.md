# Validation record

The native frontend passed model, tool, session and cancellation checks on
one Linux x86-64 setup. Functional checks used a separately configured
deployment. The portable launchers have narrower test coverage, detailed below.

## Dependency security update on 2026-10-07

The update pins oauthlib 4.0.0 and PyJWT 2.15.0. All other versions remain
unchanged, including protobuf 6.33.6. Python 3.13 dependency resolution passed
for all 57 packages. The full list was freshly installed in a separate native
frontend environment on the documented J5005 setup, with official ACP/harness
1.1.1.

| Check | Result |
| --- | --- |
| Dependency consistency | `pip check` passed |
| Existing-account authentication and model replies | Passed |
| Scratch-file write/read/delete with exact-command permissions | Passed |
| Session restoration in a fresh process | Passed |
| Two independent concurrent sessions | Passed |
| Streaming and running-tool cancellation | Cancellation, recovery and observed child cleanup passed |
| T3 Code 0.0.45 integration | Provider ready/authenticated; parallel diagnostic replies and cancellation/recovery passed without a service restart |
| Synthetic security checks | Both PyJWT advisories, JSONP removal and constant-time PKCE comparisons covered |
| OAuth client PKCE, token exchange and refresh | Passed with mocked token responses |
| Manual sign-out/sign-in through T3 Code | Reported successful on the existing test deployment |

The other authentication checks used existing account state or mocked token
responses. A forced real Google token refresh was not tested.

The test deployment also passed Gemini 3.8 Flash High coding tasks through T3:
file search/read/edit, shell commands, one-time permissions, bug fixing, seven
passing tests, CSV/JSON reports and Git review. Stopping and resuming the same
thread preserved tool operation. Cancelling an observed running shell child
removed it and allowed a subsequent read. These checks did not cover browser
or MCP tools, or force a real Google token refresh.

All eight repository preparation/launcher tests passed. Functional checks used
the separately configured native frontend; the portable launcher was not tested
with a newly prepared runtime in this checkout. Historical timings below do
not measure these new pins. This update does not patch the dependencies
embedded in full-QEMU mode.

## Historical validation

Direct ACP checks used the pinned Linux x86-64 setup described in
[performance.md](performance.md).

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

Concurrency checks used two independently launched ACP processes. They do not
establish support for arbitrary concurrent calls on one SDK Agent or harness.
This project has no shared-harness pool.

These functional results came from the pre-existing deployment. The portable
launchers were checked separately against the same pinned payload, through
initialize only, without changing an active client.

## Portable launcher checks on 2026-09-22

| Check | Result |
| --- | --- |
| Native launcher initialize | **3.179 seconds** |
| Full-QEMU launcher initialize | **44.706 seconds** |
| Protocol and server version, both paths | Protocol version 1; `agy_acp_server_1.1.1` |
| Payload verification | Both executable hashes matched; a new extraction produced 776 files |
| Local checks | Eight focused tests, Python compilation and shell syntax checks passed |

Native execution reused the validated pinned virtual environment. This was
**not a fresh package installation or a clean-machine rebuild**. Source
extraction was isolated and bytecode writes were disabled. Both processes
stopped after initialize; no model prompt or new authentication was requested.

The local tests cover preparation and launcher boundaries: hashes, archive
paths, duplicate mappings, refusal to overwrite and argument forwarding.
They do not exercise the upstream model service.

## Remaining validation

The manual T3 Code sign-out/sign-in result covers that deployment. It does not
establish fresh sign-in on a clean-machine build of the portable runtime.
Other gaps include:

- A forced real Google token refresh.
- Browser workflows, MCP tools and arbitrary external tool integrations.
- Long-running sessions.
- Other Linux distributions and Python/QEMU versions.
- Each consuming client's process lifecycle beyond the checks recorded here.

An initialize handshake alone does not validate these behaviors. This
repository distributes no account state, conversation content or raw
execution traces.
