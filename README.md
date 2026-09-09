# Purpose Execution Finality — Granular Validation Reference

Runnable, adversarial validation package for purpose-bound execution finality: Candidate Acts remain non-effective until externally grounded binding records are validated, a scoped non-bearer Execution Handle is issued, and an independent Finality Sink verifies and atomically consumes it.

## Recorded validation result

- **88/88 Python threat/unit/integration/concurrency tests passed**
- **19/19 Python conformance vectors passed**
- **19/19 Go conformance vectors passed**
- **19/19 Node.js conformance vectors passed**
- **2,000/2,000 deterministic adversarial stress trials denied as expected**
- **HMAC-SHA-256 baseline plus Ed25519 asymmetric signature variation tests**
- three measured system topologies: memory, SQLite/WAL, localhost HTTP sidecar
- three independent benchmark repetitions per topology
- concurrent single-use replay tests up to 128 simultaneous attempts / 32 workers
- explicit limitation tests for lineage stripping and compromised trusted binding records

## Primary measured p95 on recorded host

| Topology | p95 | Repository target |
|---|---:|---:|
| In-process + memory replay | 0.2106 ms | <= 5 ms |
| In-process + SQLite/WAL | 0.2560 ms | <= 10 ms |
| Localhost HTTP sidecar | 2.1363 ms | <= 20 ms |

These are **local software-reference measurements**, not protocol requirements and not TEE/HSM/GPU/WAN performance claims.

## Read first

- `GRANULAR_VALIDATION_REPORT.md` — exact test scope and defensible conclusion
- `THREAT_MODEL_MATRIX.md` — attacks, negative controls and residual risks
- `LATENCY_AND_FEASIBILITY.md` — methodology, targets, repeated measurements and exclusions
- `SYSTEM_LANGUAGE_VARIATION.md` — actually executed topology/language variants versus planned CI
- `SYSTEM_ENVIRONMENT.md` — exact environment recorded for this run
- `LICENSE-AND-PATENT-NOTICE.md` — CC BY-NC 4.0, patent reservation, IETF-essential FRAND commitment, no waiver

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e . pytest
pytest
python language_variants/python/conformance.py
go run ./language_variants/go/main.go
node ./language_variants/node/conformance.mjs
python benchmarks/benchmark_matrix.py
python benchmarks/repeat_benchmarks.py
```

## Scope discipline

This project does not claim to decide whether a purpose is legally valid. It enforces supplied machine-readable binding records. It also does not claim to prevent reuse after legitimate plaintext release, PED/binding-record compromise, or covert/side-channel exfiltration. Those limitations are documented and, where mechanically demonstrable, included as negative-control tests.
