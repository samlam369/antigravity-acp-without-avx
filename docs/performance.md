# Startup measurements

Measured on 2026-09-22 using an Intel Pentium Silver J5005 without AVX, Linux
x86-64 in a container, QEMU 10.0.13 (`-cpu max`), official ACP 1.1.1,
and native CPython 3.13.5. These are local case-study results.

## Direct ACP startup

| Stage, seconds | Full QEMU | Native frontend + QEMU harness |
| --- | ---: | ---: |
| Initialize | 45.104 | 2.423 |
| Authenticate using existing account state | 2.720 | 1.291 |
| Create session | 6.437 | 5.982 |
| Select intended model | 6.376 | 0.002 |
| Approximately ready to submit prompt | 61 | 10 |

Native initialization across the exploratory runs was 2.4–3.3 seconds.
The native row above is the final dependency pin, including protobuf 6.33.6.
The requested model was `gemini-3.8-flash-high`; only the native comparison
aligned `AGY_ACP_DEFAULT_MODEL` to it. Therefore the total improvement combines
two changes: native frontend execution and avoiding a redundant harness launch.

These timings end at prompt readiness. They do not measure client rendering,
time to first text, or completion of a coding task. Runs used fresh processes,
not a cleared operating-system cache. This was a small sequential experiment,
not a controlled statistical benchmark.

## What the original initialization was doing

The 45.104-second initialization consumed approximately 45.10 CPU seconds,
consistent with roughly one busy CPU core. Main-thread runqueue wait near
the end of that phase was only 0.043 seconds. Actual storage reads were about
123 kB, while most logical reads were satisfied from cache.

Import profiling recorded substantial Python data-model initialization:
`acp.schema` self time was 10.864 seconds and `google.genai.types` was
7.796 seconds. The full run accumulated 39.31 seconds of self import time,
including some imports after initialization; that number is not an exact
initialize-only subtotal.

The visible container CPU quota was unlimited and recorded no CPU throttling.
These observations support CPU-bound frontend initialization. They do not
exclude every host scheduler, frequency or hardware effect.

## Other options explored

| Change | Observation |
| --- | --- |
| Larger QEMU translation cache, 512 MiB | 47.898-second initialization; no improvement in this sample |
| Mask selected fast-string CPU hints | 46.682 seconds; no improvement in this sample |
| Start the ACP process before its first initialize request | Request response became quick, but expensive startup had already happened |
| Start a harness before its handshake | Handshake changed from 3.236 seconds cold to 0.070 seconds prestarted |

The last two approaches move work earlier. A dependable spare-process service
would add ownership, cancellation, replenishment and cleanup complexity.
This project implements neither. The native frontend removes much of the
actual emulated work without introducing a daemon.

## What is not established

- No guarantee of faster warm tool turns; model and network waiting still vary.
- No portable speedup factor for other processors, kernels or QEMU versions.
- No claim that all missing CPU features or every legacy x86-64 CPU are supported.
- No claim that multiple simultaneous cold starts have the same latency as one.
- No quantitative split between CPU hardware differences and QEMU overhead.

The remaining harness is still emulated. Use the measurements to understand
the startup mechanism, then measure your own complete client workflow.
