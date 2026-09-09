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

# Detailed Validation Methodology

## Purpose Execution Finality — Granular Implementation Validation

## 1. What Was Being Tested

The objective was not merely to demonstrate that a valid request can pass.

The validation was designed to test whether a consequence-bearing data operation can remain technically non-effective until all load-bearing conditions are satisfied.

The tested execution sequence was:

```text
Candidate Act
      ↓
External Binding-Record Validation
      ↓
Protected Enforcement Domain (PED)
      ↓
PASS / FAIL LAVR
      ↓
Scoped Execution Handle
      ↓
Holder Proof-of-Possession
      ↓
Independent Finality Sink Verification
      ↓
Atomic Single-Use Consumption
      ↓
Effect
```

The principal security question was:

```text
Can changing the purpose label, requester,
workload, object, operation, destination,
policy version, lineage, nonce, proof,
or replay state cause an unauthorized
operation to become effective?
```

The implementation was deliberately tested against both valid and adversarial conditions.

---

# 2. Recorded Test Environment

The validation reported in this repository was actually executed on the following environment:

| Parameter             | Recorded Value                       |
| --------------------- | ------------------------------------ |
| Validation date       | 9 September 2026                     |
| Operating system      | Linux                                |
| Kernel                | Linux 6.18.35                        |
| Architecture          | x86-64                               |
| libc                  | glibc 2.41                           |
| CPU                   | Intel Xeon Platinum 8370C @ 2.80 GHz |
| Logical CPUs visible  | 5                                    |
| Python                | 3.13.5                               |
| Python compiler build | GCC 14.2.0                           |
| SQLite                | 3.46.1                               |
| OpenSSL               | 3.5.5                                |
| Go                    | 1.23.2 linux/amd64                   |
| Node.js               | 22.16.0                              |
| Benchmark timer       | `time.perf_counter_ns()`             |

These numbers are the environment actually used.

The repository does **not** claim that these same performance figures were measured on Windows, macOS, ARM64, HSMs, TEEs, GPUs, DPUs, SmartNICs, confidential VMs, Kubernetes, WAN networks, or production advertising systems.

---

# 3. Baseline Candidate Act

A deterministic baseline scenario was used so every mutation could be compared against a known valid act.

The baseline timestamp was:

```text
1,800,000,000,000 ms
```

The Candidate Act was:

```text
version:
1

act_id:
act-001

requester_id:
delivery-service

workload_id:
delivery-workload

object_id:
address-619

workflow_id:
delivery-order-842

operation:
obtain delivery destination

destination_id:
assigned-courier-6

declared_purpose:
delivery

nonce:
nonce-001

created_ms:
1,800,000,000,000

expires_ms:
1,800,000,010,000

policy_version:
38
```

Therefore the Candidate Act validity window was:

```text
10,000 ms
= 10 seconds
```

The `declared_purpose` field is intentionally included in the Candidate Act.

However, it is deliberately treated as:

```text
UNTRUSTED REQUESTER-SUPPLIED METADATA
```

It is not itself authorization evidence.

That is important because one major test is whether simply changing:

```text
declared_purpose = delivery
```

can rescue an otherwise unauthorized advertising request.

It cannot.

---

# 4. Baseline Binding Record

The external binding record used for the valid case was:

```text
object_id:
address-619

workflow_id:
delivery-order-842

requester_id:
delivery-service

workload_id:
delivery-workload

allowed_operation:
obtain delivery destination

allowed_destination:
assigned-courier-6

policy_version:
38

valid_until:
baseline time + 60,000 ms

revoked:
false
```

The binding record therefore remained valid for:

```text
60 seconds
```

The key distinction is that this record is not generated by the requester.

The PED uses this external record to determine whether the requester's operation is actually authorized.

---

# 5. Validation Context

The baseline runtime validation context was:

```text
now_ms:
baseline + 1 ms

authenticated_requester:
delivery-service

authenticated_workload:
delivery-workload

order_exists:
true

object_association_ok:
true

recipient_assignment_ok:
true

binding_store_available:
true

binding_store_integrity_ok:
true

attestation_ok:
true

force_timeout:
false
```

Each of these fields was independently modified in negative tests.

---

# 6. Exact PED Decision Sequence

The PED uses a deterministic fail-closed evaluation order.

The following sequence is tested:

```text
1. Validation timeout?
2. Binding store available?
3. Binding store integrity acceptable?
4. Binding record exists?
5. Candidate Act still fresh?
6. Binding record still fresh?
7. Binding revoked?
8. Policy version correct?
9. Requester identity correct?
10. Workload identity correct?
11. Protected object correct?
12. Workflow correct?
13. Operation permitted?
14. Destination permitted?
15. Workflow/order exists?
16. Object belongs to workflow?
17. Recipient assignment current?
18. Required attestation valid?
```

Only after all checks succeed is the result:

```text
ALLOW
```

Any earlier failure produces:

```text
DENY
```

plus an associated failure LAVR.

One important architectural test is that:

```text
attestation_ok = true
```

does not override:

```text
OPERATION_MISMATCH
REQUESTER_MISMATCH
DESTINATION_MISMATCH
WORKLOAD_MISMATCH
```

In other words:

```text
Attested ≠ Authorized
```

---

# 7. Execution Handle Lifetime

The PED was configured with:

```text
max_handle_ms = 2000
```

Therefore a successfully issued Execution Handle is valid for at most:

```text
2 seconds
```

The actual expiration is:

```text
min(
    Candidate Act expiration,
    PED issuance time + 2000 ms
)
```

Boundary tests were run using the following candidate lifetime deltas:

| Candidate lifetime from PED time | Result                 |
| -------------------------------: | ---------------------- |
|                             0 ms | handle clamped         |
|                             1 ms | handle clamped         |
|                            10 ms | handle clamped         |
|                           100 ms | handle clamped         |
|                         1,000 ms | handle clamped         |
|                         1,999 ms | handle clamped         |
|                         2,000 ms | handle maximum reached |

The test verifies that a PED cannot accidentally issue a handle extending beyond its configured maximum or beyond the Candidate Act itself.

---

# 8. What Is Bound Into the Execution Handle

The reference Execution Handle contains:

```text
handle_id
Candidate Act digest
object_id
workflow_id
operation
requester_id
workload_id
destination_id
policy_version
nonce
issued_ms
expires_ms
proof-of-possession key ID
```

The handle therefore does not mean:

```text
"This requester may generally access this system."
```

It means approximately:

```text
"This exact Candidate Act,
for this requester,
this workload,
this object,
this workflow,
this operation,
this destination,
this policy version,
this nonce,
during this short validity window,
may be considered for effectuation
at the protected boundary."
```

---

# 9. Canonical Serialization and Candidate Act Digest

Objects are serialized using canonical JSON.

The implementation uses:

```text
sorted keys
no unnecessary spaces
UTF-8 encoding
deterministic separators
```

Conceptually:

```python
json.dumps(
    object,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False
)
```

The canonical form is hashed using:

```text
SHA-256
```

Therefore even a small change in a load-bearing Candidate Act field produces a different Candidate Act digest.

---

# 10. HMAC Baseline Cryptography

The baseline reference state machine uses:

```text
HMAC-SHA-256
```

for deterministic authentication.

Separate reference keys are used for different purposes.

PED / handle signing:

```text
ped-reference-signing-key-v1
```

LAVR chain:

```text
lavr-chain-key-v1
```

Holder 1:

```text
holder-one-key-v1
```

Holder 2:

```text
holder-two-key-v1
```

These are deliberately simple software test keys.

They are not production secrets.

Their purpose is reproducibility and transparent inspection of the protocol mechanics.

---

# 11. Ed25519 Variation

The implementation also includes a separate asymmetric cryptographic variation using:

```text
Ed25519
```

Four dedicated Ed25519 tests were executed:

| Test                                       | Expected Result |
| ------------------------------------------ | --------------- |
| Candidate Act signature round-trip         | PASS            |
| Candidate Act mutated after signing        | FAIL            |
| Execution Handle body signature round-trip | PASS            |
| Handle destination changed after signing   | FAIL            |

The Ed25519 private key is generated using the cryptography library's Ed25519 key-generation function.

This demonstrates that the canonical objects can also be authenticated asymmetrically.

It is not claimed to be an HSM-backed or TEE-protected deployment.

---

# 12. Non-Bearer Proof-of-Possession

Possession of an Execution Handle alone is deliberately insufficient.

After the PED issues the handle, the Finality Sink creates a random challenge.

Challenge generation uses:

```text
16 random bytes
```

converted to hexadecimal.

The holder then generates proof over:

```text
handle_id
Candidate Act digest
Finality Sink ID
challenge
proof-of-possession key ID
```

The baseline Finality Sink identity is:

```text
data-release-sink
```

The sink verifies both:

```text
the Execution Handle
```

and:

```text
the separate holder proof
```

before effectuation.

Therefore:

```text
Copied Execution Handle
+
No Correct Holder Proof
=
DENY
```

---

# 13. Wrong-Holder Test

Two holder keys exist:

```text
holder-1
holder-2
```

The valid handle is normally issued to:

```text
holder-1
```

The attack test generates proof using:

```text
holder-2
```

Expected result:

```text
POP_BINDING_MISMATCH
```

Another test directly modifies the PoP signature.

Expected result:

```text
POP_FAILURE
```

---

# 14. Independent Finality Sink Verification

The Finality Sink does not simply trust the fact that the PED previously returned ALLOW.

It independently performs verification.

The sink checks:

```text
Execution Handle signature
Candidate Act digest
object identity
workflow identity
operation
requester identity
workload identity
destination
policy version
nonce
authenticated requester
authenticated workload
handle expiration
source lineage
proof-of-possession binding
proof signature
single-use replay state
```

Only after all of those succeed does the system call:

```text
effect()
```

and return:

```text
EFFECTUATED
```

---

# 15. Total Python Test Count

The Python automated suite executed:

```text
88 tests
88 passed
0 failed
```

The distribution was:

| Test File                        | Executed Tests |
| -------------------------------- | -------------: |
| `test_core.py`                   |             17 |
| `test_crypto_variants.py`        |              4 |
| `test_ped_and_threats.py`        |             22 |
| `test_lineage_lavr.py`           |             11 |
| `test_replay_system_variants.py` |             10 |
| `test_variation_matrix.py`       |             24 |
| **Total**                        |         **88** |

Parameterized cases are counted individually.

---

# 16. Post-Issuance Mutation Tests

A valid Candidate Act is first authorized.

Then the Candidate Act is changed **after the Execution Handle has already been issued**.

The following fields were individually mutated:

| Field            | Example Mutation                                       |
| ---------------- | ------------------------------------------------------ |
| object           | `address-619 → other`                                  |
| workflow         | `delivery-order-842 → other`                           |
| operation        | `obtain delivery destination → infer household income` |
| destination      | `assigned-courier-6 → advertising-profile-database`    |
| requester        | `delivery-service → advertising-service`               |
| workload         | `delivery-workload → ad-workload`                      |
| declared purpose | `delivery → marketing`                                 |
| nonce            | `nonce-001 → other`                                    |
| policy version   | `38 → 39`                                              |

Because the canonical Candidate Act changes, the digest no longer matches the handle.

Expected result:

```text
ACT_DIGEST_MISMATCH
```

This prevents a previously approved handle from being reused for a materially different act.

---

# 17. PED-Side Mutation Tests

Before issuance, the Candidate Act is separately modified to test each binding relationship.

The following are explicitly tested:

```text
requester mismatch
workload mismatch
object mismatch
workflow mismatch
operation mismatch
destination mismatch
policy-version mismatch
```

Each must result in DENY.

For example:

```text
Allowed operation:
obtain delivery destination

Requested operation:
infer household income
```

Result:

```text
OPERATION_MISMATCH
```

---

# 18. Purpose-Relabel Attack

This is one of the most important threat-model tests.

An advertising workload submits:

```text
requester:
advertising-service

workload:
ad-workload

operation:
infer household income

destination:
advertising-profile-database
```

but deliberately writes:

```text
declared_purpose:
delivery
```

The authenticated context is also changed so that the requester genuinely is the advertising workload.

The question is:

```text
Can the requester obtain access merely
by writing a permitted-looking purpose?
```

Result:

```text
DENY
```

because the external binding record still says:

```text
requester = delivery-service
workload = delivery-workload
operation = obtain delivery destination
destination = assigned-courier-6
```

Changing the purpose string does not change those facts.

---

# 19. Good-Sounding Purpose Variations

The implementation tests several plausible or favorable-looking purpose strings:

```text
delivery
customer_support
legitimate_interest
consent
security
fraud_prevention
```

The requested operation remains unauthorized:

```text
infer household income
```

All are denied with:

```text
OPERATION_MISMATCH
```

This is intended to demonstrate that semantic attractiveness of a label is irrelevant to the authorization decision.

---

# 20. Declared-Purpose Independence

The legitimate delivery Candidate Act was also tested with several different declared-purpose values:

```text
delivery
DELIVERY
targeted_marketing
empty string
128-character arbitrary string
```

When all external binding records remain valid, the Candidate Act is still allowed.

This test is significant because it confirms the implementation really does ignore the requester-controlled purpose label as authoritative evidence.

The authorization result comes from the binding relationship, not the spelling of the purpose field.

---

# 21. Attestation Threat Variation

The unauthorized advertising act was tested while:

```text
attestation_ok = true
```

The request remained denied.

A second test changes only the operation while keeping:

```text
attestation_ok = true
```

Result:

```text
OPERATION_MISMATCH
```

A third test uses a valid Candidate Act but sets:

```text
attestation_ok = false
```

Result:

```text
ATTESTATION_FAILURE
```

Thus the implementation demonstrates both directions:

```text
Passing attestation does not grant authorization.

Failing required attestation can still deny authorization.
```

---

# 22. Binding-Store Failure Tests

The binding store is deliberately made unavailable:

```text
binding_store_available = false
```

Result:

```text
BINDING_STORE_UNAVAILABLE
```

The binding store is then made available but its integrity is considered uncertain:

```text
binding_store_integrity_ok = false
```

Result:

```text
BINDING_STORE_INTEGRITY_FAILURE
```

The system does not convert either condition into ALLOW.

---

# 23. Missing Binding Record

The PED is invoked with:

```text
BindingRecord = None
```

Result:

```text
NO_BINDING_RECORD
```

No Execution Handle is issued.

This implements fail-closed behavior.

---

# 24. Freshness Tests

Three independent freshness conditions are tested.

### Candidate expired

The runtime clock is moved to:

```text
Candidate expiration + 1 ms
```

Result:

```text
CANDIDATE_EXPIRED
```

### Binding record expired

The binding validity timestamp is moved to:

```text
current time - 1 ms
```

Result:

```text
BINDING_EXPIRED
```

### Handle expired

A valid handle is first issued.

Then sink verification occurs at:

```text
handle expiration + 1 ms
```

Result:

```text
HANDLE_EXPIRED
```

---

# 25. Revocation Test

The external binding record is changed to:

```text
revoked = true
```

Result:

```text
BINDING_REVOKED
```

No usable Execution Handle is issued.

---

# 26. Policy-Version Variation

The valid policy version is:

```text
38
```

The following incorrect policy versions were individually tested:

```text
0
1
37
39
40
1000
```

Every value must return:

```text
POLICY_VERSION_MISMATCH
```

---

# 27. Workflow-State Tests

The system independently tests three external workflow relationships.

### Missing workflow

```text
order_exists = false
```

Result:

```text
WORKFLOW_NOT_FOUND
```

### Wrong object association

```text
object_association_ok = false
```

Result:

```text
OBJECT_ASSOCIATION_MISMATCH
```

### Changed recipient assignment

```text
recipient_assignment_ok = false
```

Result:

```text
RECIPIENT_ASSIGNMENT_MISMATCH
```

---

# 28. Validation Timeout

The validation context can explicitly inject:

```text
force_timeout = true
```

Result:

```text
VALIDATION_TIMEOUT
```

The system does not interpret timeout as permission.

---

# 29. Derived-Data Lineage Test

A separate Candidate Act models a derived object:

```text
act_id:
act-derived

requester:
advertising-service

workload:
ad-workload

object:
income-estimate-52

workflow:
ad-profile-workflow

operation:
write advertising profile

destination:
advertising-profile-database

purpose:
advertising

source_lineage:
address-619

derived_object:
income-estimate-52
```

For this test, the PED is intentionally given a binding record that would otherwise allow the derived write.

Therefore the PED issues a valid Execution Handle.

This intentionally tests whether the Finality Sink remains independently load-bearing.

The sink examines:

```text
source_lineage = address-619
```

The protected lineage rule permits `address-619` only for:

```text
operation:
obtain delivery destination

destination:
assigned-courier-6
```

The attempted derived-data write therefore produces:

```text
LINEAGE_RESTRICTION_MISMATCH
```

even though it already has a valid Execution Handle.

---

# 30. Lineage Positive Control

The same source lineage:

```text
address-619
```

is attached to the permitted delivery Candidate Act.

Because its operation and destination match the protected lineage rule:

```text
obtain delivery destination
assigned-courier-6
```

the sink returns:

```text
EFFECTUATED
```

This confirms that lineage presence itself is not automatically a denial.

The rule depends on the intended use.

---

# 31. Lineage-Stripping Negative Control

A deliberate limitation test removes:

```text
source_lineage
```

from the derived advertising object.

The sink is then unable to infer the restricted source from arbitrary output content.

Result:

```text
EFFECTUATED
```

This is intentionally preserved in the validation package.

It demonstrates an important deployment requirement:

```text
Lineage must be protected from stripping,
or independently reconstructable.
```

The repository does not hide this limitation.

---

# 32. LAVR Generation

Every PED decision generates a LAVR.

That applies to:

```text
PASS
```

and:

```text
FAIL
```

A LAVR body contains:

```text
monotonic sequence number
previous LAVR hash
Candidate Act digest
PASS / FAIL result
reason code
policy version
timestamp
```

The LAVR body is then HMAC-authenticated.

---

# 33. LAVR Chaining

The first LAVR begins with:

```text
previous hash =
64 zero characters
```

After a LAVR is generated:

```text
SHA-256(current LAVR)
```

becomes the `prev_hash` of the next record.

The test verifies:

```text
sequence number continuity
previous-hash continuity
HMAC integrity
```

---

# 34. LAVR Tamper Test

A valid LAVR is generated.

Its signature is then deliberately changed.

Chain verification must return:

```text
false
```

The test therefore demonstrates detection of a modified reference receipt.

This is a local authenticated hash chain.

It is not represented as a public blockchain or distributed ledger.

---

# 35. Replay Test

A valid Execution Handle is used once.

First attempt:

```text
EFFECTUATED
```

The exact same handle is then used again.

Second attempt:

```text
REPLAY_DETECTED
```

---

# 36. In-Memory Replay Mechanism

The in-memory replay store uses:

```text
thread lock
+
set of consumed handle IDs
```

Consumption works conceptually as:

```text
LOCK

if handle_id already exists:
    DENY

else:
    mark used
    ALLOW

UNLOCK
```

This prevents concurrent threads in the same process from successfully consuming the same handle more than once.

---

# 37. SQLite Replay Mechanism

The persistent variation uses SQLite.

Configuration includes:

```text
PRAGMA journal_mode=WAL
```

The replay table is:

```text
used(
    handle_id TEXT PRIMARY KEY,
    used_ms INTEGER NOT NULL
)
```

Each consume performs:

```text
BEGIN IMMEDIATE
INSERT handle_id
COMMIT
```

Because:

```text
handle_id
```

is the primary key, a repeated handle causes an SQLite integrity error.

The transaction is rolled back and the attempt returns:

```text
REPLAY_DETECTED
```

---

# 38. Concurrent Replay Testing — Memory

Five simultaneous replay-pressure profiles were executed:

| Worker Threads | Attempts Using Same Handle |
| -------------: | -------------------------: |
|              2 |                         10 |
|              4 |                         32 |
|              8 |                         64 |
|             16 |                        100 |
|             32 |                        128 |

For every profile, the required invariant was:

```text
EFFECTUATED count = exactly 1

REPLAY_DETECTED count =
attempts - 1
```

All profiles passed.

---

# 39. Concurrent Replay Testing — SQLite

Four SQLite concurrency profiles were executed:

| Worker Threads | Attempts |
| -------------: | -------: |
|              2 |        8 |
|              4 |       16 |
|              8 |       32 |
|             16 |       64 |

Again:

```text
exactly one
```

attempt was allowed to consume the handle.

Every other concurrent attempt was denied as replay.

---

# 40. Persistent Replay Across Reopen

The SQLite store was also tested for restart-like persistence.

Sequence:

```text
Issue handle
↓
Successfully consume handle
↓
Close SQLite connection
↓
Reopen database
↓
Attempt same handle again
```

Expected result:

```text
REPLAY_DETECTED
```

The test passed.

This demonstrates local persistent replay state.

It is not a test of distributed multi-node replay consensus.

---

# 41. Deliberate Trusted-Record Compromise Test

One particularly important negative-control test deliberately rewrites the trusted binding record.

The attack changes the authoritative record itself to say:

```text
requester:
advertising-service

workload:
ad-workload

allowed_operation:
infer household income

allowed_destination:
advertising-profile-database
```

The PED then returns:

```text
ALLOW
```

This is intentional.

It demonstrates that:

```text
A correct PED cannot compensate
for corrupted authoritative truth.
```

Therefore the integrity of the binding-record system must be protected to at least the same assurance level as the enforcement decision.

This is documented as a residual security assumption rather than hidden.

---

# 42. Cross-Language Conformance Testing

The architecture was also tested independently in:

```text
Python 3.13.5
Go 1.23.2
Node.js 22.16.0
```

A common JSON file contains:

```text
19 deterministic conformance vectors
```

Each vector contains:

```text
Candidate Act
binding record
validation context
expected decision
expected SHA-256 Candidate Act digest
```

Each language independently canonicalizes the Candidate Act, calculates the digest, performs the core decision logic, and compares the output with the expected values.

---

# 43. The 19 Cross-Language Cases

The deterministic conformance cases are:

| Case                           | Expected Result                 |
| ------------------------------ | ------------------------------- |
| baseline valid request         | ALLOW                           |
| wrong requester                | REQUESTER_MISMATCH              |
| wrong workload                 | WORKLOAD_MISMATCH               |
| wrong object                   | OBJECT_MISMATCH                 |
| wrong workflow                 | WORKFLOW_MISMATCH               |
| wrong operation                | OPERATION_MISMATCH              |
| wrong destination              | DESTINATION_MISMATCH            |
| changed untrusted purpose only | ALLOW                           |
| wrong policy version           | POLICY_VERSION_MISMATCH         |
| revoked binding                | BINDING_REVOKED                 |
| expired binding                | BINDING_EXPIRED                 |
| missing record                 | NO_BINDING_RECORD               |
| missing workflow               | WORKFLOW_NOT_FOUND              |
| broken object association      | OBJECT_ASSOCIATION_MISMATCH     |
| changed assignment             | RECIPIENT_ASSIGNMENT_MISMATCH   |
| unavailable binding store      | BINDING_STORE_UNAVAILABLE       |
| binding integrity failure      | BINDING_STORE_INTEGRITY_FAILURE |
| attestation failure            | ATTESTATION_FAILURE             |
| forced timeout                 | VALIDATION_TIMEOUT              |

Results:

```text
Python:   19/19
Go:       19/19
Node.js:  19/19
```

Total language-vector executions:

```text
57
```

These should not be described as 57 entirely different threats.

They are 19 common semantic vectors executed independently in three languages.

---

# 44. What Cross-Language Testing Demonstrates

The result provides evidence that:

```text
canonicalization
SHA-256 digest semantics
external binding-record checks
decision ordering
reason-code behavior
```

can be implemented consistently across three common programming languages.

It does **not** mean the small Go and Node conformance programs are complete production equivalents of the Python implementation.

The complete LAVR lifecycle, replay store, sidecar server, and PoP lifecycle remain primarily implemented in the Python reference.

---

# 45. Deterministic Adversarial Stress Test

A separate stress test was run outside pytest.

The random generator was seeded with:

```text
20260909
```

This makes the test reproducible.

Total trials:

```text
2,000
```

---

# 46. Stress Group A — 1,000 Post-Issuance Mutations

One valid handle is first issued.

Then one of the following fields is randomly selected:

```text
requester_id
workload_id
object_id
workflow_id
operation
destination_id
nonce
policy_version
```

For string fields, unique random replacement values are generated.

For policy version, a random non-baseline integer is used.

Total:

```text
1,000 mutation attempts
```

Result:

```text
1,000 / 1,000 denied
```

---

# 47. Stress Group B — 500 Purpose-Relabel Attacks

For each trial, the requester is changed to:

```text
advertising-service
```

workload:

```text
ad-workload
```

operation:

```text
infer household income
```

destination:

```text
advertising-profile-database
```

A random purpose label from:

```text
0–40 random alphabetic characters
```

is generated.

Total:

```text
500 trials
```

Result:

```text
500 / 500 denied
```

---

# 48. Stress Group C — 500 Wrong-Holder Attempts

A fresh valid Candidate Act and handle are created for each trial.

Proof is deliberately generated using:

```text
holder-2
```

instead of the bound:

```text
holder-1
```

Total:

```text
500 trials
```

Result:

```text
500 / 500 denied
```

---

# 49. Total Executed Validation Volume

The validation results should be described carefully.

Actual executed groups were:

```text
88 pytest cases

57 cross-language vector executions
(19 × 3 languages)

2,000 seeded adversarial trials
```

These are different kinds of testing.

They should not simply be added together and advertised as:

```text
2,145 unique security tests
```

because some cases overlap conceptually.

A more accurate statement is:

```text
88 automated Python test cases,
19 shared conformance vectors independently
executed in three languages,
and 2,000 additional deterministic
adversarial mutation trials.
```

---

# 50. Latency Measurement Scope

Latency testing measures the execution-finality control path itself.

The measured path includes:

```text
Candidate Act validation
LAVR generation
Execution Handle issuance
holder proof generation
independent Finality Sink verification
replay/effect consumption
```

The benchmark does **not** include:

```text
actual external business effect
WAN request
remote policy database
remote attestation
HSM invocation
TEE transition
human approval
payment-network settlement
production advertising exchange
GPU/DPU transition
distributed consensus
```

---

# 51. Benchmark Clock

All measured latency uses:

```python
time.perf_counter_ns()
```

This provides a high-resolution monotonic performance timer.

Each measured duration is converted from nanoseconds to:

```text
milliseconds
```

---

# 52. Fresh Candidate Per Benchmark Iteration

Each benchmark iteration creates a new Candidate Act with:

```text
unique act_id
unique nonce
fresh created_ms
fresh expires_ms
```

This avoids benchmarking a permanently reused identical act and prevents the replay mechanism from contaminating subsequent valid iterations.

---

# 53. Topology A — In-Process Memory

The lowest-overhead topology runs:

```text
Candidate
PED
LAVR
handle
PoP
Finality Sink
memory replay store
```

inside one process.

Primary benchmark parameters:

```text
Warm-up:
300 iterations

Measured:
3,000 iterations

p95 target:
≤ 5 ms
```

Measured results:

| Statistic |    Result |
| --------- | --------: |
| p50       | 0.1678 ms |
| p95       | 0.2106 ms |
| p99       | 0.2618 ms |
| mean      | 0.1796 ms |
| max       | 3.0804 ms |

Result:

```text
PASS
```

---

# 54. Topology B — SQLite/WAL

The second topology replaces the replay state with persistent SQLite/WAL.

Primary parameters:

```text
Warm-up:
200

Measured:
2,000

p95 target:
≤ 10 ms
```

Measured:

| Statistic |    Result |
| --------- | --------: |
| p50       | 0.1987 ms |
| p95       | 0.2560 ms |
| p99       | 0.3841 ms |
| mean      | 0.2147 ms |
| max       | 2.7283 ms |

Result:

```text
PASS
```

The benchmark measures latency.

It does not claim SQLite is a hyperscale production finality backend.

---

# 55. Topology C — HTTP Sidecar

The third topology introduces a real process/HTTP boundary.

A local HTTP server listens at:

```text
127.0.0.1
```

on an automatically allocated local port.

For each request, the client serializes:

```text
Candidate Act
Binding Record
Validation Context
```

to JSON.

The request is transmitted over:

```text
TCP
+
HTTP
```

to the sidecar.

The sidecar reconstructs the objects, performs PED validation, generates the handle/proof, performs Finality Sink effectuation, and returns:

```json
{"result":"EFFECTUATED"}
```

or a denial response.

Primary parameters:

```text
Warm-up:
100

Measured:
1,000

p95 target:
≤ 20 ms
```

Measured:

| Statistic |     Result |
| --------- | ---------: |
| p50       |  1.4670 ms |
| p95       |  2.1363 ms |
| p99       |  3.7796 ms |
| mean      |  1.5826 ms |
| max       | 10.5086 ms |

Result:

```text
PASS
```

This is localhost loopback.

It is not a WAN measurement.

---

# 56. Why Different Latency Targets Were Used

One latency target for every topology would be misleading.

Therefore three repository regression targets were defined:

| Topology           | p95 Target |
| ------------------ | ---------: |
| In-process memory  |     ≤ 5 ms |
| In-process SQLite  |    ≤ 10 ms |
| Local HTTP sidecar |    ≤ 20 ms |

These are:

```text
engineering regression thresholds
```

not:

```text
IETF protocol requirements
```

and not:

```text
guaranteed production latency.
```

---

# 57. Repeated Latency Runs

The benchmark was not accepted based only on one favorable execution.

Every topology was repeated three additional times.

### Memory p95

```text
Run 1: 0.2424 ms
Run 2: 0.2154 ms
Run 3: 0.2169 ms
```

Range:

```text
0.2154–0.2424 ms
```

### SQLite p95

```text
Run 1: 0.2605 ms
Run 2: 0.4145 ms
Run 3: 0.3568 ms
```

Range:

```text
0.2605–0.4145 ms
```

### HTTP sidecar p95

```text
Run 1: 2.3466 ms
Run 2: 2.0291 ms
Run 3: 2.2572 ms
```

Range:

```text
2.0291–2.3466 ms
```

Every repeated p95 remained below its repository target.

---

# 58. Outlier Handling

No benchmark outlier was deleted simply because it looked inconvenient.

One HTTP-sidecar repeat recorded:

```text
maximum latency:
47.9501 ms
```

That result was retained.

The same run still produced:

```text
p95:
2.2572 ms
```

This distinction is important because maximum scheduler or runtime pauses can occur even where normal percentile latency remains low.

---

# 59. Why p50, p95 and p99 Are Reported

The benchmark reports:

```text
p50
p95
p99
mean
minimum
maximum
```

A median alone can hide tail behavior.

A maximum alone can be dominated by an isolated scheduler or runtime event.

Reporting multiple percentiles provides a more useful engineering picture.

---

# 60. Hot Path and Cold Path Interpretation

The measured benchmark is intended to represent the deterministic hot path.

A production architecture should generally avoid putting all expensive trust-establishment work in every request.

Examples of cold/control-path work include:

```text
policy reasoning
remote attestation refresh
key provisioning
record synchronization
large external policy lookups
human approval
```

The hot path can then verify:

```text
Candidate Act digest
current binding
freshness
revocation
holder proof
sink identity
replay state
```

before effectuation.

This does not mean the cold-path information is optional.

It means it can often be established or refreshed separately and then bound into short-lived current state.

---

# 61. What the Test Supports

The evidence supports the following bounded statement:

```text
On the recorded Linux/x86-64 environment,
the reference Candidate Act → external
binding validation → LAVR → scoped
non-bearer handle → holder proof →
independent Finality Sink → atomic
single-use effectuation path executed
correctly under the tested threat,
mutation, concurrency, storage,
language, and local-topology variations.
```

It also remained within the repository's defined p95 regression thresholds.

---

# 62. What the Test Does Not Support

The test does not prove:

```text
that all implementations are secure

that all production systems will have
sub-millisecond latency

that a TEE or HSM has the same latency

that a WAN deployment has the same latency

that lineage can never be removed

that an attacker cannot compromise
the authoritative binding database

that plaintext can never be copied after
legitimate release

that covert channels are prevented

that the protocol is formally verified

that the architecture automatically
establishes legal compliance
```

Those limitations are deliberately stated.

---

# 63. Main Residual Risks

The most important residual boundaries are:

| Residual Risk                                                  | Result                                   |
| -------------------------------------------------------------- | ---------------------------------------- |
| Authorized recipient copies plaintext after legitimate release | Not solved by source-side finality alone |
| PED itself compromised                                         | Outside the PED's own protection         |
| Trusted binding record maliciously modified                    | Can create false PASS                    |
| Derived lineage stripped before sink                           | Sink may lose provenance                 |
| Side/covert channel inside authorized computation              | Not solved                               |
| Human screenshot/observation                                   | Not solved                               |
| Software-held test key compromised                             | Reference implementation limitation      |
| SQLite single-host limitations                                 | Not hyperscale evidence                  |

These are not test failures hidden from the repository.

They are documented trust boundaries.

---

# 64. Why the Validation Is Feasibility-Oriented

The package was designed so that feasibility is not supported by one benchmark number alone.

The evidence comes from several different directions:

```text
positive functional path

fail-closed negative paths

load-bearing field mutation

cryptographic tamper detection

proof-of-possession

replay prevention

concurrent replay races

persistent replay state

lineage enforcement

negative-control limitation tests

cross-language deterministic conformance

multiple storage/topology variations

repeated latency measurements

retained outliers

explicit untested-system disclosure
```

That combination is significantly stronger than simply saying:

```text
"The implementation works."
```

---

# 65. Recommended Next-Level Validation

The current package is a software-reference feasibility demonstration.

For stronger production-grade evidence, the next validation phase should replace one software assumption at a time with a real deployment component:

1. protected or cryptographically signed external binding-record store;
2. non-exportable holder PoP key;
3. HSM- or TEE-backed Execution Handle signing;
4. replicated transactional replay/effect database;
5. actual service-mesh/API-gateway integration;
6. remote-attestation freshness and revocation integration;
7. protected lineage propagation through a real computation pipeline;
8. network-partition and stale-replica fault injection;
9. sustained concurrency and throughput measurement;
10. independent interoperable implementation using the published conformance vectors.

Only after those components are measured should stronger production claims be made.

---

# 66. Reproduction Commands

The validation package can be reproduced with:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e . pytest

pytest

python language_variants/python/conformance.py
go run ./language_variants/go/main.go
node ./language_variants/node/conformance.mjs

python stress/adversarial_stress.py

python benchmarks/benchmark_matrix.py
python benchmarks/repeat_benchmarks.py
```

The expected primary Python result is:

```text
88 passed
```

The expected language results are:

```text
Python: 19/19
Go:     19/19
Node:   19/19
```

The deterministic stress result is:

```text
1,000/1,000 post-issuance mutations denied
500/500 purpose relabels denied
500/500 wrong-holder attempts denied
```

---

# 67. Recommended GitHub Wording

A technically defensible summary is:

```text
The reference implementation was evaluated through
88 automated Python unit, integration, threat-model,
cryptographic, lineage, replay, persistence and
concurrency tests; 19 deterministic conformance
vectors independently executed in Python, Go and
Node.js; and 2,000 seeded adversarial mutation trials.

Testing covered purpose relabeling, authenticated
requester/workload substitution, operation/object/
workflow/destination mutation, policy-version
mismatch, expiry, revocation, attestation separation,
binding-store failure, derived-data lineage,
proof-of-possession, signature tampering, sequential
and concurrent replay, persistent replay state and
trusted-record negative controls.

Three local software topologies were benchmarked:
in-process memory, SQLite/WAL and localhost HTTP
sidecar. Primary measured p95 values were 0.2106 ms,
0.2560 ms and 2.1363 ms respectively on the recorded
Linux/x86-64 host.

These measurements are reference-software results,
not protocol requirements and not TEE, HSM, GPU,
WAN or production-system performance claims.
```

