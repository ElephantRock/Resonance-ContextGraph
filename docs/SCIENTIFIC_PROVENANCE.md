# Scientific provenance

Architectural independence is based on the ContextGraph experiment lineage preserved in `ElephantRock/Resonance-World`, branch `experiment/context-graph`.

This repository does not rewrite or relocate those frozen experimental records. It extracts the mechanisms that survived preregistered testing.

## Source lineage

### CG-4 — sparse endogenous graph failure

CG-4 established that the first live endogenous compiler did **not** generalize over a matched flat control. That failure remains part of the scientific record. The subsequent autopsy identified a single-positive-probe winner's-curse mechanism and weak proxy signal, motivating event reconciliation and measurement sufficiency.

### CG-5 — revised active-measurement confirmation

CG-5 confirmed the revised coverage graph under preregistered active measurement with six independent reconciled probe events per current agent/skill cell.

- protocol freeze: `2e55d858192e59e5bfbd18b937c73a937f41a054`
- confirmatory workflow: `31622647635`
- result commit: `1c56bf2533aa164e40a0073c5bc4bdeb32083510`
- fresh-source artifact: `9151913749`
- result artifact: `9151923169`

Interpretation boundary: CG-5 did not erase CG-4's sparse-evidence failure; it confirmed a revised reconciled measurement regime.

### CG-10 / CG-10B — stopping calibration

CG-10 tested observable pair-stability stopping across already-unblinded CG-5, CG-7, and CG-9 societies. The uncapped form failed its tail-cost criterion. CG-10B made exactly one exploratory repair: retain pair-stability stopping and impose a 168-probe hard cap.

The repair qualified across the previously unblinded cohorts and was frozen without further threshold tuning.

### CG-11 — fresh-cohort confirmatory stopping replication

CG-11 confirmed the frozen CG-10B stopping rule on 30 untouched societies.

Protocol:

- protocol freeze: `4b336f824f3bbcbfde425de1920dfabd6d23b738`
- evaluator freeze after lint-only correction: `fdc7368d90e5deeb5c770ad2101eca8e3f37e721`
- code-only preflight workflow: `31632376342`
- execution head: `70f41b960c51865d08bf29195ccc452f189d2bdf`
- confirmatory workflow: `31632483751`
- result commit: `280ce5fddadf290cff6fcc0f06810ceb5590166c`
- provenance record commit: `a7d41d40f5577a3db4d9c66bcd4ded7c463836e0`

Cohort:

- 30 fresh Fields
- 360 agents
- 180 decisions
- 512 trials per decision
- 92,160 trials per arm
- zero prior-seed overlap

Measurement economy:

- stopped mean probe events: `111.2`
- fixed-six mean probe events: `216.0`
- mean cost reduction: `48.52%`
- p90 stopped probe events: `168`
- maximum stopped probe events: `168`

Primary non-inferiority:

- stopped graph expected success: `0.2790790551714306`
- fixed-six expected success: `0.28111686910074246`
- stopped minus fixed-six: `-0.002037813929311849`
- Field-clustered 95% CI: `[-0.01273644855252886, 0.008471978107990202]`
- frozen non-inferiority margin: `-0.015`
- result: PASS

Topology at matched stopped cost:

- stopped graph expected success: `0.2790790551714306`
- bundle-flat expected success: `0.23579355738359445`
- graph minus flat: `+0.043285497787836164`
- Field-clustered 95% CI: `[0.024750411577349092, 0.0614619325409784]`
- shuffled graph expected success: `0.20674335731768048`
- graph minus shuffled: `+0.07233569785375013`
- shuffled contrast 95% CI: `[0.05518247320639642, 0.08976068038353197]`

Measurement quality and integrity:

- estimate/truth Pearson: `0.4220262436317142`
- invalid selection rate: `0.0`
- provenance completeness: `1.0`
- belief contamination: `0`
- historical outcome rows consumed: `0`
- post-hoc imported claims: `0`
- outcome-law graph inputs: `0`
- stopping evaluator-truth inputs: `0`

All preregistered CG-11 gates passed.

## What graduated

The standalone architecture therefore adopts the mechanisms supported by the full lineage rather than copying any single experimental script wholesale:

1. append-only provenance-bearing evidence;
2. event-identity reconciliation before statistical counting;
3. uncertainty-aware candidate/skill estimation;
4. balanced measurement instead of outcome-informed adaptive cell selection;
5. observable pair-stability sufficiency stopping with a hard cap;
6. bounded complete-unit topology-aware context compilation;
7. explicit separation of evidence, world truth, belief, social state, and outcome laws.

## What did not graduate

The following remain experimental failures or non-goals and are not promoted as validated architecture:

- sparse single-positive evidence ranking from CG-4;
- random individual-claim flat sampling as a serious flat baseline;
- hidden-truth-guided measurement acquisition;
- adaptive selection of which cell to probe based on evaluator outcomes;
- automatic belief synchronization;
- direct graph effects in environment outcome laws;
- any particular persistent graph database.
