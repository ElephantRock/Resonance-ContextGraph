# Architecture

## Purpose

Resonance ContextGraph turns heterogeneous observations into bounded, provenance-complete decision context without collapsing evidence into truth or shared belief.

The subsystem owns five transformations:

```text
raw observations
      ↓
append-only evidence claims
      ↓
event reconciliation
      ↓
uncertainty-aware evidence estimates
      ↓
bounded topology-aware context compilation
      ↓
observable measurement sufficiency / stopping
```

It does **not** own environment truth, agent belief, social state, or task outcome laws.

## Hard epistemic boundaries

```text
canonical world truth
        !=
shared evidence graph
        !=
agent-local belief
        !=
social/public graph
        !=
execution/task graph
```

These are separate state spaces and must remain separate APIs.

### World truth

Evaluator or environment state. ContextGraph may receive observations emitted from interactions with the world, but it must never read hidden evaluator truth to rank evidence, choose what to measure, decide when to stop measuring, or compile context.

### Evidence graph

Append-only provenance-bearing claims plus reconciled event identities. Evidence can be contradictory, stale, incomplete, or wrong.

### Belief

Owned by the consuming agent runtime. Retrieval from ContextGraph never mutates belief. Belief adoption requires an explicit perception, communication, or deliberation step outside this package.

### Social/public state

Public reputation, relationships, institutions, and organization memory are separate semantic domains. They may be represented as evidence claims when observed, but ContextGraph does not make them canonical truth and does not inject them into an environment's outcome law.

## Runtime modules

### `models.py`

Storage-neutral immutable evidence contracts:

- `EvidenceClaim`
- `ObserverReport`
- `EvidenceEvent`
- `MissionSpec`

Every claim carries identity, scope, provenance, observer, source class, observation time, confidence, and optional validity bounds.

### `store.py`

Deterministic append-only evidence storage. The initial implementation is intentionally in-memory and backend-neutral. Persistence is a later adapter decision.

There is deliberately no belief mutation method.

### `reconcile.py`

Collapses multiple complete observer bundles with the same event identity into one independent `EvidenceEvent`. The canonical report is selected deterministically by highest bundle confidence, then latest observation time, then observer ID. All reports remain attached, and disagreement is explicit metadata.

This prevents observer duplication from masquerading as independent statistical support.

### `estimator.py`

Scores candidate/skill cells from independent reconciled events. The validated estimator family includes posterior mean and conservative Wilson lower-bound scoring with minimum-support shrinkage/fallback.

### `compiler.py`

Builds bounded contexts from complete evidence units. It first preserves active membership, then allocates event bundles across required mission roles/candidate cells before spending residual budget on recent admissible events.

It never materializes all candidate-pair relationships. Pair utility is derived from candidate/skill topology and evidence at query time.

### `measurement.py`

Balanced round-robin measurement scheduling. It chooses only among the least-measured available cells and uses deterministic hashing to break ties. Hidden capability is not part of the interface.

### `stopping.py`

Observable sufficiency stopping. The default policy reproduces the CG-11 confirmed rule: after 60 events, stop when the six-mission selected-pair vector matches the immediately previous checkpoint; otherwise hard-stop at 168.

## Causal contract

ContextGraph is allowed to affect:

```text
evidence visible to decision process
        ↓
decision / routing / partner selection
```

ContextGraph is not allowed to affect:

```text
environment outcome law
hidden capability
canonical world state
agent belief without explicit adoption
```

A consuming runtime should therefore use an adapter boundary similar to:

```python
context = compiler.compile(request)
action = agent.decide(context)
outcome = environment.evaluate(action)
```

The environment receives the action, not the graph.

## Persistence

No graph database is selected by this extraction. The evidence contracts and compiler semantics are the architecture; persistence is an implementation adapter. A persistent backend must preserve append-only identity, provenance, event reconciliation, temporal filtering, contradiction visibility, and deterministic replay.

## Independence gate

Standalone package source must not import `resonance_world`. CI enforces this mechanically.
