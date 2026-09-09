# Granular Validation Report

## 1. Objective

This validation package tests whether the execution-finality pattern can be implemented as a deterministic, fail-closed control between a proposed data operation and the moment data is released or a derived-data write becomes effective.

The core invariant under test is:

```text
Candidate Act
  -> external binding-record validation in the PED
  -> PASS/FAIL LAVR
  -> short-lived act-bound non-bearer Execution Handle on PASS
  -> holder proof-of-possession
  -> independent Finality Sink verification
  -> atomic consume
  -> effect
```

A requester-controlled purpose string is intentionally present in the Candidate Act but is **not authoritative**. The PED derives authorization from external binding records.

## 2. Validation philosophy

The test package is designed to make overclaiming difficult:

- a positive path is not enough; every load-bearing field is mutated;
- passing attestation is tested separately from authorization;
- replay is tested sequentially and concurrently;
- derived-data lineage is enforced at the sink;
- two known trust-boundary failures are executed as explicit limitation demonstrations;
- language portability is tested with deterministic vectors;
- topology overhead is measured in three system configurations;
- benchmark outliers are retained;
- regression targets are labeled as targets, not protocol requirements;
- untested hardware/OS/deployment environments are named explicitly.

## 3. Test inventory

### Python automated suite

**88/88 tests passed.** Distribution:

- `test_core.py`: 17
- `test_crypto_variants.py`: 4
- `test_ped_and_threats.py`: 22
- `test_lineage_lavr.py`: 11
- `test_replay_system_variants.py`: 10
- `test_variation_matrix.py`: 24

These are executed pytest cases; parameterized cases count separately.

### Cross-language conformance

19 deterministic vectors were executed in each of three languages:

- Python: 19/19
- Go: 19/19
- Node.js: 19/19

That is **57 language-vector executions**, in addition to the 88 pytest cases. It should not be described as 145 unique threat scenarios; some conformance vectors deliberately overlap the core suite to verify semantic portability.


### Deterministic adversarial stress run

A separate seeded stress runner (`seed=20260909`) executed **2,000 additional adversarial trials**:

- 1,000 post-issuance mutations of requester, workload, object, workflow, operation, destination, nonce, or policy version: **1,000/1,000 denied**;
- 500 purpose-relabel attacks using randomized declared-purpose strings with an advertising requester/operation/destination: **500/500 denied**;
- 500 wrong-holder proof-of-possession attempts: **500/500 denied**.

These are repeated mutation trials, not 2,000 unique threat classes.

### Cryptographic variation

HMAC-SHA-256 is used for the deterministic baseline state machine. Four additional tests exercise an Ed25519 asymmetric signer over canonical Candidate Act and Execution Handle bodies, including mutation/tamper rejection. This demonstrates an asymmetric signing variation without claiming that the entire Python reference package is an HSM/TEE-backed Ed25519 deployment.

## 4. Baseline data-purpose scenario

The baseline mirrors the delivery-address example:

- protected object: `address-619`
- workflow: `delivery-order-842`
- authenticated requester: `delivery-service`
- workload: `delivery-workload`
- allowed operation: `obtain delivery destination`
- allowed destination/recipient: `assigned-courier-6`
- policy version: `38`
- requester-declared purpose: `delivery` (untrusted input)

The binding record, not the declared purpose, determines whether the act can advance.

## 5. Decision parameters

A PED decision checks, in fail-closed order:

1. forced timeout;
2. binding-store availability;
3. binding-store integrity status;
4. presence of a binding record;
5. Candidate Act freshness;
6. binding-record freshness;
7. revocation state;
8. policy version;
9. authenticated requester and record requester;
10. authenticated workload and record workload;
11. protected object identity;
12. workflow identity;
13. requested operation versus allowed operation;
14. destination versus assigned/allowed destination;
15. workflow/order existence;
16. object-to-workflow association;
17. current recipient assignment;
18. required attestation result.

A passing attestation is never evaluated as a substitute for items 8–17.

## 6. Non-bearer mechanics in the reference implementation

The Execution Handle is HMAC-authenticated and binds:

- handle ID;
- Candidate Act digest;
- object ID;
- workflow ID;
- operation;
- requester identity;
- workload identity;
- destination;
- policy version;
- nonce;
- issue/expiry time;
- proof-of-possession key ID.

The Finality Sink additionally requires a holder proof bound to the handle ID, Candidate Act digest, sink ID, challenge and holder key ID. Therefore copying the handle alone is insufficient in the reference protocol state machine.

The test holder key is ordinary process memory. A production non-bearer claim requires a protected/non-exportable holder key or equivalent channel/workload binding.

## 7. LAVR mechanics

A LAVR is produced for PASS and FAIL outcomes. The reference chain contains:

- monotonic sequence number;
- previous LAVR hash;
- Candidate Act digest;
- PASS/FAIL;
- reason code;
- policy version;
- timestamp;
- HMAC authentication.

Tests verify normal chaining and deliberate tamper detection. The implementation is a reference hash chain, not a public blockchain or independently replicated ledger.

## 8. Derived-data lineage

The sink has a protected rule for restricted source `address-619`. A derived advertising-profile Candidate Act can receive an otherwise valid handle in the test setup, but if its `source_lineage` contains `address-619`, the Finality Sink independently rejects the derived write because the requested operation/destination is not allowed for that source.

A separate negative-control test strips the lineage and demonstrates that the sink can no longer infer the restricted source from arbitrary content. This makes the implementation requirement explicit: provenance must be deliberate and non-removable or independently reconstructable.

## 9. Replay and atomicity

Memory replay state uses a lock-protected set. SQLite replay state uses a primary-key uniqueness constraint inside `BEGIN IMMEDIATE` / commit.

Concurrency profiles actually executed:

### Memory
- 10 attempts / 2 workers
- 32 / 4
- 64 / 8
- 100 / 16
- 128 / 32

### SQLite
- 8 attempts / 2 workers
- 16 / 4
- 32 / 8
- 64 / 16

Every profile required exactly one successful consumption and all remaining attempts to return replay denial.

SQLite persistence was also tested across close/reopen.

## 10. System topology measurements

See `LATENCY_AND_FEASIBILITY.md` and JSON result files for complete numbers. Primary p95 values on the recorded host:

- in-process memory: **0.2106 ms** (target <=5 ms)
- in-process SQLite: **0.2560 ms** (target <=10 ms)
- localhost HTTP sidecar: **2.1363 ms** (target <=20 ms)

Three independent repeats were also run for every topology. Maximum observed values are retained; no outlier removal was applied.

## 11. Feasibility conclusion that the evidence supports

The results support a bounded engineering statement:

> On the recorded Linux/x86-64 host, the reference Candidate Act -> external binding validation -> LAVR -> act-bound handle -> proof-of-possession -> Finality Sink -> atomic replay/effect path executed correctly under the tested threat and concurrency variations, produced consistent decisions across Python/Go/Node conformance vectors, and remained within the repository's non-normative p95 regression targets for in-process memory, in-process SQLite, and localhost HTTP-sidecar topologies.

The results **do not support** a claim that every real production deployment, TEE/HSM implementation, distributed database, WAN topology, advertising exchange, or regulatory use case will have the same latency or security properties.

## 12. Limitations that must remain visible

- plaintext legitimately released to an authorized recipient can be copied outside the enforced path;
- PED compromise is outside the protection supplied by the PED itself;
- authoritative binding-record compromise can create a false PASS;
- source lineage must be protected from stripping;
- side/covert channels are not solved;
- HMAC and holder keys in this reference are software-held test secrets;
- SQLite is a demonstration backend, not a hyperscale architecture;
- localhost HTTP is not a WAN/distributed measurement;
- no formal proof or model checking is included;
- no legal compliance determination is performed;
- no TEE/HSM/GPU/DPU performance claim is made.

## 13. Recommended next validation layers

For an adopter wanting stronger evidence, the next steps are not broader prose claims but replacement of one assumption at a time with a measured component:

1. external signed/attested binding-record store;
2. non-exportable PoP key;
3. HSM/TEE-backed handle signing;
4. replicated transactional replay/effect backend;
5. service-mesh/gateway integration;
6. remote attestation freshness/revocation integration on the cold path;
7. controlled lineage propagation through a real computation runtime;
8. failure-injection under network partition and stale-replica conditions;
9. sustained throughput and tail-latency testing;
10. independent implementation interop using the deterministic vector set.
