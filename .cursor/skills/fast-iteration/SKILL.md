---
name: fast-iteration
description: >-
  Fast claim-harness iteration — reuse flags, single-job runs, cache
  discipline, honest labeling of dev shortcuts. Use when developing or
  debugging a claim gate before the official tools/run.py pass.
---

# Fast Iteration (Claim Development)

Rule hooks: `verification-lifecycle.mdc` (official pass only via
`tools/run.py`), `metric-integrity.mdc` (label dev shortcuts honestly).

The official run happens once, at the end. During harness development, cut
long wall-clocks down with the patterns below — and never report their
numbers as verified results.

## 1. Reuse flags (`<PREFIX>_REUSE=1`)

Pattern inside a claim's `run.py`:

```python
if os.environ.get("MYCLAIM_REUSE") == "1" and artifact.is_file():
    return json.loads(artifact.read_text())  # skip the expensive leg
```

- Prefix = short claim mnemonic.
- Reuse only when the cached artifact is still valid for the edit under test.
- Document in the module docstring: `Reuse: MYCLAIM_REUSE=1`.

## 2. Single jobs (`--job <name>`)

When a claim gate has multiple expensive legs (several datasets, several
configurations), wire a `--job` flag from day one so one leg can run alone:

```bash
python3 <claim-folder>/run.py --job smoke10
```

## 3. Cache and environment discipline

- Pin the same input versions (dataset, fixtures, dependency lockfile)
  across iteration — a changed pin invalidates every comparison.
- Do not regenerate derived snapshots/config artifacts unless inputs
  actually differ — every new snapshot is a cache miss and a comparability
  break.
- After config edits, diff the effective configuration before re-running
  the expensive legs.

## 4. Shared resources

If gates compete for a scarce resource (a database, a device, a port, a
license), reserve before the run and release after — see the
`parallel-workers` skill. Do not start a heavy leg "because it looked
free".

## New claim checklist

When authoring a new `<claim-folder>/run.py`:

1. `--job <name>` for each expensive leg
2. `<PREFIX>_REUSE=1` + artifact skip at the top of each leg function
3. Docstring lists jobs, reuse flag, expected runtime
4. `last_run.json` written atomically (see `tools/lib/registry.py::atomic_write_json`)
5. Official pass: no reuse, full job list, `python3 tools/run.py <CLAIM>`

## Anti-patterns

- Re-running the full matrix after a one-line gate change without `--job`
- Reporting reuse/subset numbers as verified metrics
- Editing the harness and the feature in the same iteration step (you can
  no longer attribute the delta)
