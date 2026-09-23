# Literature and novelty audit

Search date: 23 September 2026. Primary papers were retrieved from arXiv,
author-hosted PDFs, ACL Anthology and publisher sites. PDFs used for close
reading are recorded by URL and SHA-256 in source_manifest.json; copyrighted
reference PDFs are temporary working files and are not redistributed.

## Search scope

Query families included LLM debate + bifurcation/consensus/dynamical systems;
LLM agent memory + feedback/hysteresis/provenance; selective verification +
budget/scheduling/pulse; majority rule + optimal control; opinion dynamics +
bang-bang/zealots/resetting; finite consensus + limit laws/critical window.
This is a scoped, date-stamped review, not an exhaustive systematic review or
a patent clearance search. A negative search cannot establish universal priority.

## Closest antecedents and separation

| Primary work | Relevant established result | Difference in this project |
| --- | --- | --- |
| Galam (2002), arXiv:cond-mat/0203553 | Local majority opinion dynamics and tipping | Majority response and bistability are background, not claimed inventions |
| Kumar, Sahasrabudhe & Moharir (MTNS 2018), pp. 134--141 | Asynchronous binary urn with budgeted directed influence, including perfect replacements; early-versus-late finite-horizon scheduling | This is the closest scheduling antecedent. The mechanism and timing question are established. Our contribution targets autonomous post-intervention absorption risk and its fixed-count occupancy-plus-escape critical window. Their symmetric quadratic flip rule even has the same mean-field drift as our majority reader, but a different transition variance |
| d'Amore & Ziccardi, arXiv:2112.03543 | Phase transition under noisy 3-majority communication | Directed truth resets replace entire updates; noise is not symmetric communication corruption |
| Becker & Panagiotou (2026), arXiv:2605.19131v2 | Gaussian winning-opinion law and runtime distributions for synchronous nonlinear consensus | The winning-opinion boundary layer is an antecedent. Here asynchronous one-slot updates are composed with a fixed-count verification pulse, yielding the occupancy-plus-escape variance and a check-budget quantile |
| Kozitsin (2022 preprint; 2024 journal version), arXiv:2207.01300 | Optimal control of opinion distributions with stubborn agents; bang-bang structure | Pulse structure is not new in control. We solve a specific minimum-fuel crossing objective and distinguish peak capacity from total reset budget |
| Nugent, Gomes & Wolfram (2024), arXiv:2404.09849 | Control by modifying evolving network edge weights | Our control replaces selected node updates, with a different feasible set and cost |
| Grange (2023), arXiv:2207.08590 | Voters reset to initial opinions under Poisson clocks; steady-state analysis | Resets are to the correct value, stop after an exactly counted pulse, and are assessed by later absorption |
| Du et al., arXiv:2305.14325 | Multiagent language-model debate improves selected reasoning tasks | No claim to invent debate; the experiment is a narrower register-reconciliation protocol |
| El et al. (2026), arXiv:2608.16578v2 | Empirically fitted statistical mechanics of interacting LLM communities | Dynamic laws for agents are already studied. Our target is verification timing and finite-population recovery budgets, not general opinion prediction |
| Denisov-Blanch et al. (2026), arXiv:2603.06612 | Correlated LLM errors limit polling-based truthfulness | Motivates external evidence; does not provide the reset-pulse budget law studied here |
| Evans (2024 lecture notes), control.course.pdf | Bang-bang control and verification arguments | Mathematical machinery acknowledged; our scalar lower bound is derived in full |
| Darling (2002), arXiv:math/0210109 | Fluid approximation of jump processes | Supports the mean-field setting; the discrete pulse variance explicitly respects a fixed update count |

## Candidate topics rejected or narrowed

General phase transitions in LLM debate were rejected as too close to El et al.
General provenance-aware memory was rejected as crowded: examples include
FARMA/SENTINEL (arXiv:2607.05029), RoMeRL (arXiv:2608.02508), and recent
ACL memory-management systems. A generic retry-queue instability study was
not pursued because conventional retry storms and feedback control would be
the primary explanation without a clear new mathematical target.

## Defensible contribution

The narrow proposed contribution is the combination of an explicit
minimum-fuel law, a finite-state verification-pulse certificate, and a
fixed-count critical-window law with two separable variance terms, together
with a controlled two-model experiment that includes a monostable contrast.
The critical-window composition is the strongest candidate for mathematical
novelty found in this review. All components use established probability and
control techniques. External expert review may identify additional prior art.

## Required architectural baselines

An authoritative answer that can be broadcast and committed to every slot
eliminates all error with one source lookup and N writes. This dominates the
restricted random-address protocol in source-query cost. Sampling distinct
slots also changes the problem and improves the pulse. The manuscript must
include both facts and must not advertise a universal optimal tool-query
algorithm, an improvement in foundation-model reasoning, or a patent finding.
