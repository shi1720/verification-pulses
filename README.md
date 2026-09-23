# Verification pulses in nonlinear AI registers

Research by **Shivam Gupta**, Independent Researcher.

This project studies when concentrating a fixed verification budget can
escape a self-reinforcing error state. It contains proofs, exact finite-state
calculations, numerical experiments, and a controlled language-model study.
The experiment is a synthetic operational register with an authoritative
source, not an evaluation of an existing production memory product.

## Reproduce

```sh
uv venv .venv
uv pip install --python .venv/bin/python -r requirements-lock.txt
.venv/bin/python -m pytest -q
```

The protocol and dated amendments are in `protocol/`. Recorded model outputs
are the evidence; calling a remote model again may produce different answers.
Credentials are never part of the artifact. The API runners accept the
`OPENAI_API_KEY` environment variable or a `--key-file` outside this repository.

The target conference is SIAM DS27 (contributed lecture). Submission status
will be recorded separately; a public repository is not a publication or an
acceptance. The full manuscript and reproduction instructions are being
completed. All numerical claims must be traceable to saved outputs.
