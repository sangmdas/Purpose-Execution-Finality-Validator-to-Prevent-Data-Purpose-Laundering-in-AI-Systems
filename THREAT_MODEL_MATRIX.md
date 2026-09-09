# Threat-Model Validation Matrix

The matrix distinguishes **closed within the tested enforcement boundary**, **detected only when required metadata/state is trustworthy**, and **explicit residual risk**. This distinction is intentional: feasibility is more credible when limitations are demonstrated rather than hidden.

| ID | Threat / variation | Test method | Expected result | Status / boundary |
|---|---|---|---|---|
| T01 | Purpose relabeling | Advertising-like act claims `declared_purpose=delivery` while requester/operation/destination disagree with binding record | DENY | Tested |
| T02 | Good-sounding self-asserted purposes | `consent`, `security`, `legitimate_interest`, etc. with unauthorized operation | DENY | Tested |
| T03 | Attested but unauthorized workload | `attestation_ok=true`, wrong requester/workload/operation | DENY | Tested; attestation is not authorization |
| T04 | Attestation failure where required | `attestation_ok=false` | DENY | Tested |
| T05 | Derived-data laundering | Valid handle for derived ad-profile write carries `source_lineage=address-619` | DENY at Finality Sink | Tested |
| T06 | Lineage stripping | Producer removes lineage before sink | Demonstrates inability to infer lineage from content | Tested as explicit limitation demonstration |
| T07 | Cross-requester replay | Correct act/handle, authenticated requester changes | DENY | Tested |
| T08 | Cross-workload replay | Correct act/handle, authenticated workload changes | DENY | Tested |
| T09 | Destination substitution | Destination changed before PED or after issuance | DENY | Tested |
| T10 | Operation substitution | Operation changed before PED or after issuance | DENY | Tested |
| T11 | Object substitution | Object identifier changed | DENY | Tested |
| T12 | Workflow substitution | Workflow identifier changed | DENY | Tested |
| T13 | Policy-version rollback/substitution | Candidate carries wrong policy version | DENY | Tested |
| T14 | Expired Candidate Act | Current time exceeds Candidate Act expiry | DENY | Tested |
| T15 | Expired binding record | Binding validity expired | DENY | Tested |
| T16 | Revoked binding | `revoked=true` | DENY | Tested |
| T17 | Binding store unavailable | Required external record source unavailable | DENY | Tested fail-closed |
| T18 | Binding store integrity uncertain | Integrity signal false | DENY | Tested fail-closed |
| T19 | Validation timeout | Forced timeout | DENY | Tested fail-closed |
| T20 | Missing order/workflow | External workflow state missing | DENY | Tested |
| T21 | Object/workflow association failure | Address not associated with order | DENY | Tested |
| T22 | Recipient assignment changed | Courier assignment no longer matches | DENY | Tested |
| T23 | Handle signature tamper | HMAC changed | DENY | Tested |
| T24 | Proof-of-possession tamper | PoP signature changed | DENY | Tested |
| T25 | Wrong PoP holder | Proof produced by another holder key | DENY | Tested |
| T26 | Handle replay after successful consume | Same handle reused | DENY | Tested |
| T27 | Concurrent replay race, memory | 10–128 simultaneous consumes, 2–32 workers | Exactly one succeeds | Tested across five concurrency profiles |
| T28 | Concurrent replay race, SQLite | 8–64 simultaneous consumes, 2–16 workers | Exactly one succeeds | Tested across four profiles |
| T29 | Persistent replay after process/store reopen | Consume, reopen SQLite, retry handle | DENY | Tested |
| T30 | LAVR omission on deny | Generate failed Candidate Act | FAIL LAVR must exist | Tested |
| T31 | LAVR chain tamper | Modify stored LAVR signature | Chain verification fails | Tested |
| T32 | Requester-controlled binding record | Trusted binding record maliciously rewritten | May allow | Explicit residual-risk demonstration; record integrity is a security assumption |
| R01 | Legitimate plaintext copied after release | Outside enforced path | Not guaranteed preventable | Explicitly out of scope |
| R02 | PED compromise | PED itself attacker-controlled | Not solved by this layer | Explicitly out of scope |
| R03 | Trusted binding-record compromise | Authoritative records attacker-controlled | Can forge a passing evaluation | Explicitly out of scope unless separately protected |
| R04 | Side/covert channel inside authorized computation | Exfiltration bypasses modeled release path | Not solved | Explicitly out of scope |
| R05 | Human screenshot/observation | Physical/human path | Not solved | Explicitly out of scope |

## Why the negative controls matter

Two tests intentionally demonstrate a limitation rather than a prevention result:

1. If a producing workload can remove source-lineage metadata before the enforced boundary, a sink that has no other provenance source cannot reconstruct the missing lineage from arbitrary output content.
2. If the binding record accepted as authoritative has itself been maliciously rewritten, a correct PED can evaluate the wrong truth and allow the act.

These are not hidden test failures. They are executable demonstrations of the trust boundary described by the architecture.
