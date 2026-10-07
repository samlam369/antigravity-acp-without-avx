# Background and sources

This project documents how to run the official standalone Antigravity ACP
server on tested hardware without AVX, and how to reduce its startup time. It
provides launch scripts and a reproducible setup. Start with the
[setup guide](setup.md) for installation; this page explains the approach and
its limits.

Reviewed 2026-09-22. The service-access assessment below was reviewed separately
on 2026-09-23.

## What this project changes

Users download the official server and prepare it locally. This repository
supplies scripts, dependency pins and test results. It does not distribute
an Antigravity runtime or implement a replacement ACP server. The official
server still handles the Agent Client Protocol (ACP), with its matching harness.

There are two execution modes:

- **Full QEMU:** run the official package under QEMU user-mode emulation.
- **Hybrid:** run the Python frontend natively and the harness under QEMU.
  This preserves the extracted source files and harness binary, but changes
  the packaging, Python interpreter and dependencies.

Hybrid mode needs compatibility checks and maintenance. Calling it a simple
wrapper would hide those changes. Neither mode is an official no-AVX build.
The results apply to the tested configuration. They do not guarantee speedups
or support for every older CPU or future release.

## How this differs from an ACP adapter

A CLI-to-ACP adapter translates between ACP and a command-line tool. An
SDK-based frontend adds its own ACP interface and agent configuration. This
project instead changes how the official standalone server runs. It is not
tied to a particular editor.

Adapters can still depend on native executables. Their programming language
alone does not tell you whether they work without AVX. Check the exact runtime
version, permissions, system instructions and session lifecycle. Measure the
time to a complete response too: fast initialization may just delay runtime
startup until the first prompt. Alternatives may work well, but this project
does not establish their CPU compatibility or equivalent behavior.

## Service-access assessment

Based on the implementation and upstream documentation reviewed on 2026-09-23,
we have not identified a specific basis for concluding that this project's local
compatibility adaptations alone introduce a Terms of Service violation.

The adaptations retain the official standalone ACP implementation and matching
harness, including upstream authentication and service-access code. They add no
separate login flow, service proxy, or mechanism to bypass account entitlements
or quotas. Full QEMU changes instruction execution. Hybrid mode also changes
frontend packaging, interpreter and dependencies. These facts support our
assessment; we do not claim that the entire runtime is unchanged.

Google's [terms](https://antigravity.google/terms) and
[FAQ](https://antigravity.google/docs/faq) describe restrictions on third-party
service access, while its
[IDE documentation](https://antigravity.google/docs/ide/extensions) also describes
official integrations with non-Google editors. Editor ownership alone does not
settle whether an integration is permitted.

The reviewed documents do not specifically address QEMU execution or this hybrid
adaptation. The third-party-access clause is broad. The absence of a specific
prohibition is not an explicit exemption or Google approval. Our assessment
concerns what this compatibility layer itself adds. It does not establish that
every ACP client, account arrangement or use is permitted. It also does not
resolve all licensing questions about local extraction and adaptation. See
[licensing boundaries](../LICENSE-NOTICE.md).

## When to replace this setup

An official native release that works on your hardware removes the main reason
for this adaptation. A tested alternative may also suit you better. Before
replacing a working setup, check tools, permissions, session restoration,
cancellation and concurrent operation, as well as performance.

## Sources

- [Official ACP registry manifest](https://raw.githubusercontent.com/agentclientprotocol/registry/main/antigravity-acp/agent.json):
  identifies Google's standalone server, Linux command and release archive.
  It lists a proprietary license. This manifest is the primary distribution
  reference.
- [Official IDE extension overview](https://antigravity.google/docs/ide/extensions):
  describes integrations with multiple editors.
- [ACP stdio transport](https://agentclientprotocol.com/protocol/v1/transports):
  defines the client/server transport boundary.
- [QEMU user-mode documentation](https://www.qemu.org/docs/master/user/main.html):
  explains application emulation and interaction with the host kernel.
- [Upstream SDK report: CPUs without AVX support](https://github.com/google-antigravity/antigravity-sdk-python/issues/147):
  reports an AVX-dependent executable in the SDK wheel. This project has not
  independently verified its build-flag or broad hardware claims.
- [Upstream CLI/IDE CPU-feature issue](https://github.com/google-antigravity/antigravity-cli/issues/359):
  concerns different executables. The reporter's proposed CPU baseline is a
  hypothesis; it does not validate this project's standalone ACP target.
- [Standalone ACP 1.1.1 startup report](https://discuss.ai.google.dev/t/acp-server-1-1-1-official-agy-acp-server-cold-starts-in-16s-on-every-windows-spawn/183427):
  a community report on Windows startup and model-switch restarts. Its Windows
  packaging explanation is not the explanation for the Linux measurements here.

Third-party CLI-to-ACP adapters also use names such as `antigravity-acp` and
`agy-acp`. Their architecture and installation commands differ from the official
`agy_acp_server.par` used here. Use the registry entry and Google download URL
to identify the official release; a package name alone is not enough.
