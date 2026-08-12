# Resonance ContextGraph

**Status:** architectural independence established; `architecture/v0.1` is the first standalone runtime extraction.

Resonance ContextGraph is the provenance-bearing evidence, reconciliation, measurement-sufficiency, and bounded context-compilation subsystem extracted from the Resonance World ContextGraph research program.

Its central invariant is:

```text
world truth != evidence graph != agent belief != social/public state
```

ContextGraph may change **what evidence a decision process can inspect**. It must not silently mutate an agent's beliefs, promote evidence into canonical world truth, or directly modify an environment's outcome law.

## What lives here

```text
raw observations
      ↓
EvidenceClaim        append-only provenance
      ↓
EventReconciler      one independent event per event identity
      ↓
Estimator            uncertainty-aware candidate/skill evidence
      ↓
ContextCompiler      bounded complete-unit topology-aware retrieval
      ↓
BalancedRoundRobin   evidence acquisition without hidden truth
      ↓
PairStabilityStopper observable sufficiency stopping
```

The package has **no dependency on Resonance World**. World integration belongs behind adapters so the environment receives decisions/actions, never graph state.

## Validated defaults

The default stopping policy reproduces the CG-11 confirmatory design:

- balanced round-robin evidence acquisition;
- checkpoints at `48, 60, 72, 96, 120, 144, 168` supplemental events;
- earliest stop at 60 when the selected-pair vector exactly matches the immediately preceding checkpoint;
- hard stop at 168;
- no evaluator-truth input to acquisition or stopping.

CG-11 confirmed this policy on 30 untouched societies: mean measurement fell from `216.0` to `111.2` probes per Field (`48.5%` reduction) while meeting the frozen non-inferiority criterion. At matched stopped context cost, topology-aware retrieval exceeded bundle-flat by `+4.33 pp` expected mission success and shuffled topology by `+7.23 pp`.

See [`docs/SCIENTIFIC_PROVENANCE.md`](docs/SCIENTIFIC_PROVENANCE.md) for the complete lineage, including failed experiments that remain failures.

## Development

```bash
python -m pip install -e '.[dev]'
ruff check src tests
pytest -q
```

CI additionally rejects any standalone source reference to `resonance_world`.

## Architecture

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

The persistent graph backend is intentionally unspecified. The architecture is the evidence contract, reconciliation semantics, uncertainty model, measurement discipline, and bounded compiler—not a particular database.

## Source research

The frozen experimental lineage remains in `ElephantRock/Resonance-World`, branch `experiment/context-graph`. Those records are not being moved or rewritten as part of this extraction.
