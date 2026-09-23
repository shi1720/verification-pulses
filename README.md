# Verification Pulses and the Cost of Escaping Wrong Consensus

**Shivam Gupta · Independent Researcher · 23 September 2026**

Research artifact for asynchronous nonlinear consensus with external verification.
The implementation is named **BasinPulse**. The main result gives a recovery
budget with a deterministic `N log(x0/b)` term and a `sqrt(N)` risk margin,
combining repeated-target uncertainty and subsequent autonomous amplification.

- [Full paper](output/pdf/verification-pulses.pdf)
- [Portable arXiv source](output/arxiv-source.tar.gz)
- [Literature and novelty audit](protocol/literature_review.md)
- [SIAM DS27 submission record](submission/status.md)
- [Computed results](data/processed/)

## Mathematical example

For 16 slots, 14 initially wrong, majority-of-three ordinary updates, perfect
checks, and uniform random targets sampled with replacement:

| Budget rule | Checks | Meaning |
|---|---:|---|
| First integer above mean-field threshold | 9 | About 52.37% eventual recovery |
| Exact 95% recovery budget | 23 | Eventual wrong consensus at most 0.05 |
| Two-term asymptotic approximation | 18.93 | Scaling approximation; insufficient as a small-N certificate |

These are model-conditional results. The paper credits earlier influence
scheduling, consensus limit laws, opinion control, and stochastic resetting.
The proposed novelty is the fixed-count pulse/escape variance composition,
not the general idea of timing an intervention.

## Recorded experiment

Two pinned snapshots, `gpt-4.1-mini-2025-04-14` and
`gpt-4.1-nano-2025-04-14`, reconcile three prior reports about generated binary
operational records. There are 96 development calls, 768 calibration calls,
and 12,528 held-out trajectory calls: **13,392 terminal requests**. The 108
episodes use 18 paired task records per model, three schedules, 16 slots,
128 updates, and 12 perfect checks each. Checks are deterministic local reads;
ordinary responses are real API outputs.

The code and amended main-study protocol were publicly committed at
[`d7247ff`](https://github.com/shi1720/verification-pulses/commit/d7247ff)
before calibration and held-out evaluation. All four declared primary
comparisons are reported, including intervals that include zero. Pilot data
are excluded from inference. Protocol amendments and arithmetic corrections
remain visible rather than being rewritten.

## Offline reproduction

Python 3.12 was used. From the repository root:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python -m pytest -q
.venv/bin/python scripts/analyze.py
.venv/bin/python scripts/audit_raw.py
.venv/bin/python scripts/audit_tails.py
.venv/bin/python scripts/write_paper_tables.py
```

These commands make **no model API calls**. Analysis rebuilds five figures and
CSV tables. The raw audit reconstructs every slot update from response JSON,
checks prompts and random streams, verifies request hashes, and compares
independently reconstructed metrics with the analysis outputs. Numerical tests
check exhaustive slot transitions, a separate linear committor solve,
enumerated pulse targets, and asymmetric critical-window scaling.

With [Tectonic](https://tectonic-typesetting.github.io/) installed:

```sh
.venv/bin/python scripts/build_paper.py
```

Alternatively extract the portable archive into an empty directory and run
`pdflatex main.tex` twice. The archive contains the manuscript, generated tables,
and vector figures; data and software remain in this repository.

## Exact budget calculator

```sh
.venv/bin/python -m verification_pulses.budget --n 16 --wrong 14 --risk 0.05
.venv/bin/python -m verification_pulses.budget --n 16 --wrong 14 --risk 0.05 --distinct
```

The JSON output includes the selected budget, its exact model risk, and the
risk at the preceding budget. The distinct-target option uses a different
addressing contract and a hypergeometric survivor distribution.

## Optional new API experiment

Recorded outputs are the evidence. A new remote run is stochastic and need
not reproduce those responses. Use a **fresh working copy with an empty
`data/raw/` directory** when deliberately collecting a new experiment; do not
overwrite or mix the released records. Existing request IDs are resumed only
when their request hashes agree.

```sh
export OPENAI_API_KEY='your-own-key'
.venv/bin/python scripts/run_calibration.py --pilot
.venv/bin/python scripts/run_calibration.py
.venv/bin/python scripts/run_trajectories.py
```

Alternatively pass `--key-file /path/outside/repository`. Credentials are never
written to response logs. New API calls can incur charges. The frozen protocol
specifies counts, stopping rules, retries, seeds, and analysis decisions.

## Interpretation and practical use

This is a synthetic mechanism experiment, not a production-agent benchmark.
Its hidden truth is random, so ordinary reconciliation cannot discover fresh
evidence. A direct authoritative lookup and broadcast solves that constructed
task more cheaply. The calculator is relevant when an existing system has the
restricted update interface studied here.

Absorption guarantees require a specified response with absorbing endpoints;
a fitted LLM curve does not establish those assumptions. Nano exhibits endpoint
innovation, so its evaluation uses finite-horizon predictions. The work does
not establish patentability or production performance, and submission does not
imply conference acceptance.

## Repository map

- `src/verification_pulses/`: dynamics, calculator, task generator, API recorder
- `scripts/`: collection, analysis, raw audit, manuscript build
- `tests/`: mathematical and calculator checks
- `protocol/`: prospective plan, amendments, literature review, source hashes
- `data/raw/`: append-only responses and complete episode histories
- `data/processed/`: numerical outputs and audit results
- `figures/`: vector PDF and PNG publication figures
- `paper/`: manuscript and generated numerical macros
- `output/`: final paper and arXiv source archive
- `submission/`: abstract, metadata, and verified submission status

Code is MIT licensed. Cite the artifact using `CITATION.cff`. The manuscript
contains a computational-assistance declaration and contribution boundaries.
