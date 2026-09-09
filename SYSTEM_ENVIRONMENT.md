# System Environment Used for the Published Validation Run

This file records the environment actually used for the results committed with this repository. It is not a list of supported platforms and must not be read as a hardware certification.

| Parameter | Recorded value |
|---|---|
| Date | 2026-09-09 |
| OS/kernel | Linux 6.18.35 x86_64 |
| libc | glibc 2.41 |
| CPU | Intel(R) Xeon(R) Platinum 8370C CPU @ 2.80 GHz |
| Logical CPUs visible | 5 |
| Python | 3.13.5, GCC 14.2.0 build |
| SQLite | 3.46.1 |
| OpenSSL | 3.5.5 |
| Go | 1.23.2 linux/amd64 |
| Node.js | 22.16.0 |
| Benchmark clock | `time.perf_counter_ns()` |

## What was actually executed here

- Python unit/integration/threat/concurrency suite: 88/88 passed.
- 19 deterministic conformance vectors in Python: 19/19 passed.
- Ed25519 asymmetric signature variation: 4/4 pytest cases passed.
- Deterministic adversarial stress: 2,000/2,000 expected denials.
- The same 19 vectors in Go: 19/19 passed.
- The same 19 vectors in Node.js: 19/19 passed.
- In-process memory replay benchmark.
- In-process SQLite/WAL replay benchmark.
- Single-host HTTP loopback sidecar benchmark.
- Three independent repetitions of each benchmark topology.

## What was NOT actually executed here

No result in this repository should be represented as measured on Windows, macOS, ARM64, a TEE, HSM, TPM, confidential VM, GPU, DPU, SmartNIC, Kubernetes cluster, service mesh, remote attestation service, WAN, production RTB exchange, payment network, or distributed transactional database. A GitHub Actions matrix is included to make cross-OS/software-runtime execution easy, but those CI jobs are not reported as completed measurements unless GitHub itself records a successful run.
