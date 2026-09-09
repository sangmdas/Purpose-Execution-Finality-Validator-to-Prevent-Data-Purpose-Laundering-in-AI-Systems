# Latency, Topology, and Feasibility Validation

## Measurement rule

Only measurements produced on the recorded host are called **measured**. Values for real TEEs, HSMs, remote attestation, distributed databases, WAN links, production advertising exchanges, or other hardware are not projected from these numbers.

The benchmark includes Candidate Act validation, LAVR generation, scoped handle issuance, holder proof generation, independent Finality Sink verification, and replay/effect consumption. It excludes any real external business effect, WAN request, remote policy lookup, remote attestation handshake, HSM call, or human approval.

## Topology A — in-process, memory replay state

Primary run: 3,000 measured iterations after 300 warm-up iterations.

- p50: 0.1678 ms
- p95: 0.2106 ms
- p99: 0.2618 ms
- mean: 0.1796 ms
- max observed: 3.0804 ms
- repository regression target: p95 <= 5 ms
- result: PASS

Three-repeat p95 range (2,000 measured + 200 warm-up each run): **0.2154–0.2424 ms**. All repeats passed the 5 ms repository target.

## Topology B — in-process, SQLite/WAL persistent replay state

Primary run: 2,000 measured iterations after 200 warm-up iterations.

- p50: 0.1987 ms
- p95: 0.2560 ms
- p99: 0.3841 ms
- mean: 0.2147 ms
- max observed: 2.7283 ms
- repository regression target: p95 <= 10 ms
- result: PASS

Three-repeat p95 range (1,500 measured + 150 warm-up each run): **0.2605–0.4145 ms**. All repeats passed the 10 ms repository target.

This result is a latency measurement, not a throughput guarantee. SQLite remains a single-host/single-writer reference backend and is not presented as a production-scale finality database.

## Topology C — localhost HTTP sidecar emulation

The requester serializes the Candidate Act, binding record, and validation context as JSON and sends them over TCP/HTTP to a `127.0.0.1` sidecar process boundary. The sidecar performs PED validation and Finality Sink effectuation and returns the result.

Primary run: 1,000 measured iterations after 100 warm-up iterations.

- p50: 1.4670 ms
- p95: 2.1363 ms
- p99: 3.7796 ms
- mean: 1.5826 ms
- max observed: 10.5086 ms
- repository regression target: p95 <= 20 ms
- result: PASS

Three-repeat p95 range (750 measured + 75 warm-up each run): **2.0291–2.3466 ms**. All repeats passed the 20 ms target. One run contained a 47.9501 ms maximum outlier; it is retained rather than removed. The percentile remained within target.

This is a **single-host loopback emulation**, not a distributed-service measurement. It demonstrates that serialization + localhost transport + the reference finality path are feasible in the measured environment; it does not predict WAN or cross-region latency.

## Why three different latency targets are used

A single number would hide materially different system costs. These targets are repository engineering thresholds, not protocol requirements:

| Variant | p95 regression target | Reason |
|---|---:|---|
| In-process + memory | <= 5 ms | Detect major regression in the pure reference state machine |
| In-process + SQLite | <= 10 ms | Allow persistent atomic replay/effect commit overhead |
| Local HTTP sidecar | <= 20 ms | Allow serialization, kernel networking, HTTP and process-boundary overhead |

The target is deliberately looser than the current measurement. A target is not a claim that every deployment will meet it.

## Latency-constrained deployments

For systems with an end-to-end budget such as ~100 ms, the credible design is not to perform every expensive trust-establishment operation per request. Policy reasoning, remote attestation refresh, key provisioning, and high-cost record synchronization belong on a cold/control path where their results can be bound to short-lived current state. The hot path should perform deterministic Candidate Act matching, freshness/revocation checks, holder proof, and atomic Finality Sink consumption.

A deployment that puts fresh remote attestation, remote policy reasoning, or human approval in every 100 ms transaction must benchmark that design directly; this repository makes no claim that such a topology fits the budget.

## What would be needed for a production feasibility claim

Before claiming production feasibility, repeat these measurements on the actual target with:

- real binding-record databases and cache miss behavior;
- expected concurrency and queue depth;
- the actual HSM/TEE/confidential-computing transition;
- actual service mesh/API gateway hops;
- real clock/freshness mechanism;
- persistent, replicated replay/effect state;
- failure injection for network partitions and stale replicas;
- peak and sustained throughput;
- CPU/memory utilization;
- p50/p95/p99/p99.9 and maximum;
- restart/recovery and transactional ambiguity tests.
