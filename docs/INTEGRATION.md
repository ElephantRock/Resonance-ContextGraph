# Integration Contract

Resonance ContextGraph is consumed through dependency inversion. A world/runtime may emit observations into ContextGraph and may consume compiled evidence context from it, but ContextGraph must not import or own the world/runtime.

## Dependency direction

```text
producer / world runtime
        |
        | EvidenceClaim
        v
Resonance ContextGraph
        |
        | CompiledContext / selected measurement cell / stop decision
        v
consumer decision layer
        |
        | action / routing / partner choice
        v
environment outcome law
```

The allowed dependency direction is:

```text
Resonance World -> Resonance ContextGraph
Resonance ContextGraph -X-> Resonance World
```

## Producer adapter

A producer maps an observed assertion to `EvidenceClaim` without exposing hidden evaluator state.

Required mappings:

- stable `claim_id`;
- `scope_id` for the society/session/field;
- subject, predicate, and object;
- observer and source provenance;
- observation time;
- confidence;
- optional validity bounds.

For the current Resonance World research substrate, the canonical mapping is:

```text
LiveClaim.field_id     -> EvidenceClaim.scope_id
LiveClaim.source_id    -> EvidenceClaim.claim_id
LiveClaim.subject      -> EvidenceClaim.subject
LiveClaim.predicate    -> EvidenceClaim.predicate
LiveClaim.object       -> EvidenceClaim.object
LiveClaim.observed_by  -> EvidenceClaim.observed_by
LiveClaim.source_id    -> EvidenceClaim.source_id
LiveClaim.source_class -> EvidenceClaim.source_class
LiveClaim.observed_at  -> EvidenceClaim.observed_at
LiveClaim.confidence   -> EvidenceClaim.confidence
LiveClaim.direct       -> EvidenceClaim.direct
```

`source_id` is claim-unique in the frozen W3 endogenous evidence substrate, so using it as `claim_id` preserves exact event-bundle identity while retaining original provenance.

The adapter must not transfer any of the following into ContextGraph APIs:

- `practice_by_skill` or other hidden capability state;
- evaluator truth labels;
- oracle pairs;
- historical task outcomes used only for evaluation;
- environment objects or outcome-law callbacks;
- implicit agent-belief state.

## Decision adapter

The consumer converts a public task/mission to `MissionSpec` and `ContextRequest`, then compiles evidence:

```python
context = compiler.compile(request)
pair = context.best_pair(estimator)
```

`pair` is decision input. The environment receives only the resulting action/selection, never `EvidenceStore`, `CompiledContext`, graph topology, confidence metadata, or measurement state.

## Measurement actuator boundary

`BalancedRoundRobin` chooses *which observable agent/skill cell should be measured next*. It does not execute the measurement and has no access to hidden capability.

The consuming world/runtime is responsible for:

1. executing the selected measurement interaction;
2. observing the resulting public evidence;
3. emitting new `EvidenceClaim` rows;
4. re-entering ContextGraph through the evidence API.

This separation prevents the measurement controller from becoming an evaluator-truth oracle.

## Stopping boundary

`PairStabilityStopper` consumes only checkpoint observables, principally the compiled selected-pair vector and supplemental event count. It must never inspect evaluator truth, oracle regret, hidden capability, or realized future outcomes.

## Belief boundary

ContextGraph retrieval is evidence access, not belief adoption. A consuming agent may explicitly deliberate on or adopt retrieved evidence, but that transition belongs to the agent/belief subsystem and must be a separate operation.

There is deliberately no belief mutation API in this package.

## Parity requirements for Resonance World graduation

The duplicate experimental implementation in Resonance World may be retired only after the standalone package passes parity against the frozen experimental semantics.

Required parity gates are:

1. identical active membership candidate sets;
2. identical reconciled independent event identities;
3. identical canonical event interpretation under duplicate/conflicting observers;
4. identical conservative cell scores for the frozen estimator;
5. identical selected complete evidence events under the 48-claim coverage compiler budget;
6. identical selected partner pair for every frozen mission/checkpoint;
7. identical balanced round-robin next-cell choice;
8. identical CG-11 stopping budget per Field;
9. no World hidden/evaluator state crossing into ContextGraph;
10. no ContextGraph object crossing into `JointEnvironment.evaluate`.

Only after these gates pass should Resonance World delete its duplicate compiler/reconciliation/stopping implementation. The frozen CG experiment records themselves remain in Resonance World permanently as scientific provenance.
