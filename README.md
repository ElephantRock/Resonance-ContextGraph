# Resonance ContextGraph

**Status:** architectural independence established; runtime extraction in progress.

Resonance ContextGraph is the provenance-bearing evidence, reconciliation, measurement-sufficiency, and bounded context-compilation subsystem extracted from the Resonance World ContextGraph research program.

Its central invariant is:

```text
world truth != evidence graph != agent belief != social/public state
```

ContextGraph may change **what evidence a decision process can inspect**. It must not silently mutate an agent's beliefs, promote evidence into canonical world truth, or directly modify an environment's outcome law.

The validated research lineage remains preserved in `ElephantRock/Resonance-World` on `experiment/context-graph`. This repository is the architectural graduation target; experimental records remain immutable in their source repository.

Development begins on `architecture/v0.1` before any integration into Resonance World.
