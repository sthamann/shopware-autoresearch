# Fixed benchmark harness

Sacred, harness-owned measurement surface for the three performance research
strands. Experiments **must not** edit these scripts or configs to pass gates —
propose harness changes as a separate `VERIFY.META.*` claim first.

| Strand | Path | Primary scalar |
|---|---|---|
| Request-Performance | `request/` | p95 total response time on fixed request set |
| API-Performance | `api/` | p95 per API family on fixed endpoints |
| Katalog-Skalierung | `scale/` | p95 admin/store flows at ≥ 100k products |

## Laws

1. **Fixed inputs** — URLs, payloads, concurrency, and warmup are in each
   strand's `config.json`.
2. **Honest corpus** — scale bench reports `product_count`; gates requiring
   ≥ 100k fail until `seed_corpus.sh` has run.
3. **Stdlib only** — bench scripts use `curl` and `python3` stdlib (Pawl
   philosophy).
4. **JSON output** — each `run_bench.sh` prints one JSON object to stdout with
   `p50_ms`, `p95_ms`, `request_count`, and strand-specific fields.
5. **Docker stack** — benches target `http://localhost:8000` on the dev compose
   stack (`./scripts/dev-up.sh`).

## Usage

```bash
./verification/bench/request/run_bench.sh
./verification/bench/api/run_bench.sh
./verification/bench/scale/run_bench.sh
```

Official claim gates invoke these via each claim's `run.py`.
