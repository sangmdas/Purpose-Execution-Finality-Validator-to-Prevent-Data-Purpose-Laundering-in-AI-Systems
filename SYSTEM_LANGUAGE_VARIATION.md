# System and Language Variation

## Actually executed system variations

1. **Single process + in-memory atomic replay state** — lowest-overhead reference topology.
2. **Single process + SQLite/WAL persistent replay state** — local persistence and unique-handle atomic consume.
3. **Local HTTP sidecar topology** — JSON serialization and TCP/HTTP loopback around the complete reference decision/effect path.
4. **Concurrent replay pressure** — memory and SQLite stores exercised with multiple worker counts and simultaneous reuse of a single handle.
5. **Store reopen** — a handle consumed before SQLite close/reopen remains consumed afterward.

These variations address different engineering questions; they do not constitute different hardware platforms.

## Actually executed language variations

The repository contains 19 deterministic conformance vectors. Each vector includes a Candidate Act, external binding record/context, expected PED decision, and expected SHA-256 digest over canonical JSON.

| Runtime | Version on recorded host | Result |
|---|---|---:|
| Python | 3.13.5 | 19/19 |
| Go | 1.23.2 | 19/19 |
| Node.js | 22.16.0 | 19/19 |

All three languages independently matched both the decision result and Candidate Act digest for all 19 vectors.

### What this proves

It is evidence that the tested canonicalization and core binding-record decision semantics can be expressed consistently across three common implementation languages.

### What this does not prove

It does not prove that the Go or Node programs are full production implementations of the Python reference package. They are intentionally small conformance implementations. They do not independently reproduce the complete LAVR store, replay store, PoP lifecycle, or sidecar service.

## Cross-OS CI matrix included but not claimed as measured

The GitHub Actions workflow executes the Python suite and language vectors on Ubuntu, macOS and Windows with multiple Python versions. Until GitHub records those jobs as successful, they are **planned/automatable test coverage**, not results produced in the local validation environment.
