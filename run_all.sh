#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH=src
pytest -q
python language_variants/python/conformance.py
go run ./language_variants/go/main.go
node ./language_variants/node/conformance.mjs
python stress/adversarial_stress.py
python benchmarks/benchmark_matrix.py
python benchmarks/repeat_benchmarks.py
