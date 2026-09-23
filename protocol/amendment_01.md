# Amendment 01: fixed API count and finite-size theorem

2026-09-23, after the 96-call development pilot, before calibration or live
evaluation calls. The pilot had 96/96 valid outputs. Wrong-response counts by
wrong-peer count were mini [0,0,11,12]/12 and nano [1,3,10,11]/12. These
development outcomes suggested a stronger majority response for mini; both
models are retained, and all pilot calls remain excluded from inference.

Correct an arithmetic error in the initial call plan: 24 tasks x 3 schedules
x 116 ordinary updates x 2 models requires 16,704 calls, exceeding the stated
15,000-call ceiling. Use 18 held-out tasks, balanced six per domain, for all
three schedules and both models. This requires 12,528 trajectory calls;
together with 768 calibration and 96 pilot calls the total is 13,392.
N=16, initial wrong count 14, horizon 128 and 12 checks remain unchanged.
All 3,888 deterministic verification operations are separately counted.
No endpoint observations from calibration or live trajectories informed this
amendment. No power-based stopping or sample extension is planned.

Add an analytical critical-window result to the theory: the leading
logarithmic basin-crossing budget receives an order-sqrt(N) correction with
distinct pulse-occupancy and post-pulse escape variances. This was derived
before evaluating calibration or live trajectories and checked against exact
finite-state calculations at N=64,256,1024.
