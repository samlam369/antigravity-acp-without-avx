# Startup measurements

On one tested non-AVX machine, hybrid mode reduced prompt readiness from about
**61 seconds to 10 seconds**. This combines native Python execution with a
matching default model. It measures startup, not model response speed.

Measured on 2026-09-22: Intel Pentium Silver J5005 without AVX, Linux x86-64
in a container, QEMU 10.0.13 (`-cpu max`), official ACP 1.1.1 and native
CPython 3.13.5. These are local case-study results.

## Direct ACP startup

| Stage, seconds | Full QEMU | Native frontend + QEMU harness |
| --- | ---: | ---: |
| Initialize | 45.104 | 2.423 |
| Authenticate using existing account state | 2.720 | 1.291 |
| Create session | 6.437 | 5.982 |
| Select intended model | 6.376 | 0.002 |
| Approximately ready to submit prompt | 61 | 10 |

Native initialization took 2.4–3.3 seconds across the exploratory runs.
The native results use the final dependency pin from those runs, including
protobuf 6.33.6. These timings predate the 2026-10-07 dependency update in
[validation.md](validation.md#dependency-security-update-on-2026-10-07).

The requested model was `gemini-3.8-flash-high`. Only the native comparison
set `AGY_ACP_DEFAULT_MODEL` to that model, avoiding a second harness launch.
The total improvement therefore cannot be attributed to native execution alone.

Runs used fresh processes without clearing the operating-system cache. This
was a small sequential experiment, not a controlled statistical benchmark.
It did not measure client rendering, time to first text or coding-task completion.

## What the original initialization was doing

The 45.104-second initialization used about 45.10 CPU seconds: roughly one
busy CPU core. Main-thread runqueue wait near the end was only 0.043 seconds.
Actual storage reads were about 123 kB; most logical reads came from cache.

Import profiling showed substantial Python data-model initialization:

- `acp.schema`: 10.864 seconds of self import time.
- `google.genai.types`: 7.796 seconds of self import time.
- Profiled run: 39.31 seconds of self import time, including some imports
  after initialization. This is not an initialize-only subtotal.

The container's visible CPU quota was unlimited, with no recorded throttling.
These observations support CPU-bound frontend initialization. They do not
rule out every host scheduler, frequency or hardware effect.

## Other options explored

| Change | Observation |
| --- | --- |
| Larger QEMU translation cache, 512 MiB | 47.898-second initialization; no improvement in this sample |
| Mask selected fast-string CPU hints | 46.682 seconds; no improvement in this sample |
| Start the ACP process before its first initialize request | The request returned quickly, but expensive startup had already happened |
| Start a harness before its handshake | Handshake changed from 3.236 seconds cold to 0.070 seconds prestarted |

The last two options move work earlier. A spare-process service would also need
ownership, cancellation, replenishment and cleanup rules. This project does
not implement either option. Native execution removes much of the frontend's
emulated work without adding a daemon.

## Limits

These results do not establish:

- Faster warm tool turns; model and network waiting still vary.
- The same speedup on other processors, kernels or QEMU versions.
- Support for every missing CPU feature or legacy x86-64 CPU.
- The same latency for multiple simultaneous cold starts.
- A quantitative split between CPU hardware differences and QEMU overhead.

The harness still runs under QEMU. Measure your complete client workflow on
your own machine.
