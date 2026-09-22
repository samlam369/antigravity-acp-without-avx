# Research, terminology and project direction

Reviewed 2026-09-22. The project is framed around the standalone ACP server,
not a particular editor or a general-purpose rewrite of Antigravity.

## Recommended direction: practical compatibility toolkit

Lead with the problem and an executable recipe: run the official standalone
ACP distribution on tested Linux x86-64 hardware without AVX. Provide the
full-QEMU baseline, the native-frontend optimization, a pinned manifest and
maintenance instructions. Keep the architecture and measured limitations
close to the quick start.

The chosen name, **antigravity-acp-without-avx**, states the intended use
directly. Search wording in descriptions can include `agy_acp_server`,
`localharness_external`, `QEMU user-mode`, `SIGILL`, `illegal instruction`,
`no AVX`, `non-AVX CPU` and `Agent Client Protocol`.

Two other viable directions:

- **Case-study first:** a reproducible engineering investigation, with scripts
  supporting the article. This makes a smaller compatibility promise, but
  readers must work harder to find the operational entry point.
- **Broader compatibility toolkit:** a framework for future CPU or packaging
  adaptations. This offers room to grow, but would imply a wider test and
  maintenance scope than this one pinned implementation currently supports.

The practical toolkit with a detailed case study is the best fit for the
working code and evidence available now.

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

Use “unofficial execution compatibility wrapper,” “native Python frontend with
an emulated harness,” and “measured on the tested configuration.”
Avoid “official no-AVX build,” “universal legacy CPU support,” “feature-check
bypass,” or guaranteed speedups. Unchanged packaged source files do not make
the altered execution environment an official supported build.
