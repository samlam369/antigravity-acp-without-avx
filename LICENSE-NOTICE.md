# Licensing and component boundaries

The license for this project's original scripts and documentation has not yet
been selected. This private draft does not currently grant a general
open-source license; select one before public release.

The official standalone ACP distribution is identified as proprietary in its
[registry manifest](https://raw.githubusercontent.com/agentclientprotocol/registry/main/antigravity-acp/agent.json),
which links to [Google's terms](https://antigravity.google/terms).
This project contains no Google executable or extracted packaged source.
Users acquire the official release directly and prepare their local copy.

The [public Antigravity Python SDK license](https://github.com/google-antigravity/antigravity-sdk-python/blob/main/LICENSE)
is Apache-2.0. That does not establish a license for every module and resource
inside the standalone ACP archive.

[QEMU is GPLv2](https://www.qemu.org/docs/master/about/license.html), with some
parts under other licenses. QEMU and dependency packages are separately
acquired components; their licenses are not replaced by a future license for
this repository. Their binaries and environments are excluded from Git.

This is an unofficial compatibility experiment. It makes no claim of Google
endorsement or a determination that all deployment arrangements are permitted
by upstream terms. Review the applicable upstream terms and component notices
when deciding how to use or distribute your own work.
