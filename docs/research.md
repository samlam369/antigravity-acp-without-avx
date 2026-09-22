# Research, terminology and project direction

Reviewed 2026-09-22. The project is framed around the standalone ACP server,
not a particular editor or a general-purpose rewrite of Antigravity.

## Adopted position: compatibility strategy with reference tooling

A practical compatibility and startup optimization strategy for the official
standalone Antigravity ACP server, accompanied by executable reference tooling
and a reproducible engineering case study.

The project supplies launchers, verified local preparation, dependency pins
and engineering evidence. It does not supply a third-party ACP server build,
implement a replacement ACP server, or redistribute a prebuilt upstream
runtime. Users acquire the official payload and apply the strategy locally.
The value is execution compatibility while reusing the official protocol
implementation and matching harness.

The two reference paths are full QEMU user-mode emulation and hybrid execution:
native Python frontend + QEMU-emulated harness. The latter preserves extracted
source bytes and the harness binary, but changes packaging and dependencies.
That adaptation has a real compatibility and maintenance surface; describing
it as a transparent or maintenance-free wrapper would overstate its guarantees.

The chosen name, **antigravity-acp-without-avx**, states the intended use
directly. Search wording in descriptions can include `agy_acp_server`,
`localharness_external`, `QEMU user-mode`, `SIGILL`, `illegal instruction`,
`no AVX`, `non-AVX CPU` and `Agent Client Protocol`.

## Why this is distinct from an ACP adapter

CLI-to-ACP adapters implement protocol/session/event mapping around a CLI.
SDK-based ACP frontends implement their own ACP interface and agent
configuration on top of an SDK. Both may still depend on native executables;
the language of the outer adapter does not determine CPU compatibility.
This project's reference implementation concerns the execution environment,
while the upstream server continues to supply the ACP implementation.

An alternative may become preferable, but assess its exact runtime version,
permissions, system instructions, session lifecycle and complete response
latency. Fast adapter initialization can simply defer native runtime startup
until the first prompt. No blanket claim is made that alternatives fail on
non-AVX hardware or behave identically to the standalone server.

## Service-access assessment

Based on the implementation and upstream documentation reviewed on 2026-09-23,
we have not identified a specific basis for concluding that this project's local
compatibility adaptations alone introduce a Terms of Service violation. The
adaptations retain the official standalone ACP implementation and matching
harness, including upstream authentication and service-access code. They add no
separate login flow, service proxy, or mechanism to bypass account entitlements
or quotas. Full QEMU changes instruction execution; hybrid mode also changes
frontend packaging, interpreter and dependencies. These are the technical grounds
for our assessment, rather than a claim that the entire runtime is unchanged.

Google's [terms](https://antigravity.google/terms) and
[FAQ](https://antigravity.google/docs/faq) describe restrictions on third-party
service access, while its
[IDE documentation](https://antigravity.google/docs/ide/extensions) also describes
official integrations with non-Google editors. Editor ownership alone is not
sufficient to classify an integration. The reviewed documents do not specifically
address QEMU execution or this hybrid adaptation. The third-party-access clause
is broad, so the absence of a specific prohibition is not an explicit exemption.
Our assessment concerns what this compatibility layer itself adds; it does not
establish that every ACP client, account arrangement or use is permitted, or
resolve all licensing questions about local extraction and adaptation. See
[licensing boundaries](../LICENSE-NOTICE.md).

## Scope and retirement criteria

The engineering case study supports the executable recipe, without promising
universal legacy-CPU support or compatibility with arbitrary future releases.
Keep the pinned baseline and validation limits close to the setup instructions.

An official native release that works on the target hardware removes the
main reason for this adaptation. A tested alternative can also supersede it
if its behavior and performance better fit the user's requirements. Validate
tools and permissions, restoration, cancellation and concurrent operation
before retiring the known-working environment. Reimplementing the ACP server
is not a project objective.

## Product boundaries and sources

- [Official ACP registry manifest](https://raw.githubusercontent.com/agentclientprotocol/registry/main/antigravity-acp/agent.json):
  identifies Google's standalone server, Linux command and release archive.
  It lists a proprietary license. This manifest is the primary distribution
  reference.
- [Official IDE extension overview](https://antigravity.google/docs/ide/extensions):
  describes integrations across multiple editors. The execution adaptation
  can remain independent of a specific client.
- [ACP stdio transport](https://agentclientprotocol.com/protocol/v1/transports):
  defines the client/server transport boundary.
- [QEMU user-mode documentation](https://www.qemu.org/docs/master/user/main.html):
  explains application emulation and interaction with the host kernel.
- [Upstream SDK report: CPUs without AVX support](https://github.com/google-antigravity/antigravity-sdk-python/issues/147):
  a user report about the SDK wheel containing an AVX-dependent executable,
  using the same symptom and hardware terminology as this project. Its build
  flag and broad hardware claims are not independently established here.
- [Upstream CLI/IDE CPU-feature issue](https://github.com/google-antigravity/antigravity-cli/issues/359):
  demonstrates the vocabulary users encounter around missing instructions.
  It concerns different executables, and the reporter's proposed CPU baseline
  is a hypothesis, not validation of this project's standalone ACP target.
- [Standalone ACP 1.1.1 startup report](https://discuss.ai.google.dev/t/acp-server-1-1-1-official-agy-acp-server-cold-starts-in-16s-on-every-windows-spawn/183427):
  a community report on Windows startup and model-switch restarts. Its Windows
  packaging explanation is not the explanation for the Linux measurements here.

Projects named `antigravity-acp` or `agy-acp` also exist as third-party
CLI-to-ACP adapters. Their architecture and installation commands differ from
the official `agy_acp_server.par` distribution used here. Identify the
official release by the registry entry and Google download URL, not only a
package name.

## Claims to keep precise

Use “compatibility and startup optimization strategy with reference tooling,”
“unofficial execution compatibility layer,” “hybrid execution: native Python
frontend + QEMU-emulated harness,” and “measured on the tested configuration.”
Use “wrapper” for the individual launchers, not as the complete description
of the extraction and dependency adaptation.
Avoid “official no-AVX build,” “universal legacy CPU support,” “feature-check
bypass,” or guaranteed speedups. Unchanged packaged source files do not make
the altered execution environment an official supported build.
