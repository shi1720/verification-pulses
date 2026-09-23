# Research plan, version 1

Recorded 2026-09-23 before any study API calls. This is a prospective local
protocol, not a registered report or external preregistration.

## Question and scope

Can a bounded number of external checks be more effective when concentrated
into a pulse than when spread across updates of a self-reinforcing shared
register? Separate minimum-fuel basin escape, finite-population absorption,
and measured language-model response behavior. Do not assert that all debate
or all agent memories follow a majority model.

The deployment abstraction is a register replicated across N mutable slots.
At an update, one slot is selected uniformly. An ordinary reconciliation reads
three independent slot samples (with replacement) and writes an LLM-produced
binary answer. A verification update reads an authoritative deterministic
source and writes its value directly. Updates are serial within each episode;
independent episodes may run concurrently. Correctness is externally known.

## Mathematical targets

1. Characterize constant-verification saddle nodes for majority-of-three.
2. Derive minimum verification cost to cross an unstable equilibrium for a
   general scalar response curve, with a peak-rate cap and imperfect checks.
3. Derive finite-N pulse survival law, exact absorption probabilities, and a
   computable certificate for a pulse followed by ordinary updates.
4. Identify when a global pulse recommendation is not warranted: monostable
   response, weak verifier, limited peak capacity, recurrent innovations, or
   incorrect scalar closure. Include an operation-order counterexample.

## Experimental phases

Development pilot: 12 generated tasks, three operational domains, four peer
compositions, two pinned model snapshots. Inspect parser reliability and the
shape of the response curve. Pilot data are excluded from held-out analysis.
Models: gpt-4.1-mini-2025-04-14 and gpt-4.1-nano-2025-04-14, temperature 0.7.
If a snapshot is unavailable, record the failure and explicitly amend the plan
before replacement. No silent substitutions.

Calibration: 96 independently generated tasks (32/domain), four compositions
(0,1,2,3 wrong peer reports), both models. Each task/condition has one API call.
Randomize semantic answer labels and peer order. Estimate four response
probabilities and their Bernstein polynomial. Bootstrap whole tasks, not
individual conditions, for uncertainty. No fake independent replications.

Live held-out trajectories: initially 24 new tasks (8/domain) per model;
N=16, initial wrong count 14, 128 updates, 12 verification updates. Compare
an initial pulse, 12 evenly spread checks, and a final pulse. An optional
unverified comparison and larger sample may be added in a dated amendment
before those calls. Use exactly the same update-target and peer-index streams
across schedules for each task, but retain actual independent model responses.
All schedules have the same count of ordinary and verification updates.
Primary endpoint: wrong fraction at update 128. Also report path-integrated
wrong fraction and wrong-consensus occupancy. Do not conflate final error and
long-run basin escape. Report all contrasts, including unfavorable results.
Paired task bootstrap (10,000 replicates) with family adjustment for two models
and the two pulse-versus-spread comparisons; show raw paired observations.

Numerical experiments: integrate the exact mean-field equation, propagate
finite-N transition matrices, and simulate independent chains. Vary population,
initial contamination, verifier error, pulse size, and peak verification rate.
Deterministic and stochastic calculations are not empirical LLM observations.

## Provenance and stopping

Save exact request JSON, successful API response JSON, returned model and
response IDs, timestamps, failures, token usage, task seed and code revision.
Keep credentials outside the repository. Retry transport failures at most
three times; never retry a valid but unfavorable answer. Invalid responses
retain the current slot in a trajectory and are reported separately. For
calibration, report valid-only estimates and worst-case invalid bounds.
All logs are append-only and resumable by unique request ID. Cap request count
at 15,000 and estimated API usage at USD 15 unless a new explicit budget is
obtained. Small synthetic inputs only; no private data in requests.

## Novelty and publication

Classical majority dynamics, saddle nodes, minimum-fuel control, and finite
birth-death chains are established. The proposed contribution is a specific
verification scheduling law, its finite-population calibration, and direct
tests in a reproducible LLM reconciliation system. Compare with recent agent
dynamics, opinion control, zealot models, and verifier-based inference.
Absence from searched literature does not prove priority or patentability.
DS27 receives an abstract, not this full manuscript. Never describe submission
or acceptance without the actual confirmation record.
