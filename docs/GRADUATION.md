# Architectural Graduation Record

Resonance ContextGraph earned runtime ownership through exact replay parity against the frozen Resonance World research lineage. This record is architectural provenance, not a new scientific efficacy claim.

## Tested runtime

- Repository: `ElephantRock/Resonance-ContextGraph`
- Runtime commit used by World parity: `55ce7bb435b3d4a1ff888474a5ca76ccff843150`
- Independent standalone CI: `31637686651` — success
- Independence gate: no `resonance_world` reference or dependency under standalone `src/`

## World parity gate

- Repository: `ElephantRock/Resonance-World`
- Branch: `experiment/context-graph`
- Workflow: `31638124103` — success
- Result artifact: `9157806653`
- Artifact digest: `sha256:3a333eb1b502c78c03e237d9bebe4a6249b13ed9aefee9082b3baa0894e79249`
- Exact World result commit: `e19703a40e0070c34a7e8e9f424d5cb0b31db134`

The workflow verified the original source-capsule hashes before replaying either experiment.

## CG-5 replay

- 15 Fields
- 90 decisions
- 0 context mismatches
- exact expected success: `0.27763600681086903`
- exact context size: `47` claims / `13` complete events per decision
- exact supplemental acquisition: `3240` probe events

## CG-11 replay

- 30 Fields
- 180 final decisions
- 210 checkpoint observations compared
- 1260 checkpoint context decisions compared
- 360 stopped/fixed final contexts compared
- 5040 balanced scheduler steps compared
- 0 context mismatches
- 0 checkpoint-observable mismatches
- 0 scheduler mismatches
- 0 stopping mismatches
- exact mean stop: `111.2` supplemental events
- exact stop histogram: `60:8, 72:4, 96:3, 120:4, 144:2, 168:9`
- exact stopped expected success: `0.2790790551714306`
- exact fixed-six expected success: `0.28111686910074246`
- exact context size: `47` claims / `13` complete events per decision

## Extraction findings

### Delivery identity is not provenance identity

The frozen W3 evidence generator can emit a provenance `source_id` repeatedly when the participant is also the scout for an event. ContextGraph therefore requires a delivery-unique `claim_id` while preserving the producer's `source_id` unchanged as provenance. After confidence filtering, the last admissible same-observer predicate delivery wins; complete reports from multiple observers are reconciled to one independent event.

### Executed CG-11 stopping contract includes score margin

The CG-11 preregistration prose described pair-vector stability as the stopping criterion. The frozen evaluator additionally computed minimum selected-role event support and minimum selected-role score margin, and `choose_stop` enforced thresholds `support >= 0` and `margin >= 0.0`. The support threshold is vacuous; the score-margin threshold is not.

The historical preregistration and result are not rewritten. Runtime compatibility follows the executed frozen evaluator because that implementation generated the confirmatory result. The discrepancy is explicitly preserved here and in Resonance World.

## Ownership boundary

ContextGraph now owns:

- evidence contracts and append-only evidence semantics;
- event reconciliation;
- uncertainty-aware estimation;
- bounded topology-aware context compilation;
- balanced measurement scheduling;
- observable sufficiency stopping.

Resonance World owns:

- world/environment dynamics;
- action and outcome laws;
- adapters from observed World events to ContextGraph claims;
- immutable research configs, runners, results, and replay fixtures.

Duplicate runtime implementation in World is authorized for **deprecation**, not immediate deletion. It remains available until downstream imports migrate and then remains as needed for scientific replay. Frozen experiment records remain permanently immutable.
