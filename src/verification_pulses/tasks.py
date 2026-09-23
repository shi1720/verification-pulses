"""Seeded operational register records; public synthetic inputs only."""
from __future__ import annotations
import random

DOMAINS = ["feature", "warehouse", "routing"]
SYSTEM = (
    "You reconcile an operational record from prior assistant reports. "
    "The reports can be stale or wrong. Infer the most plausible current value "
    "using the information provided. You have no tools in this reconciliation "
    "step. Return only the requested JSON; do not invent additional evidence."
)


def make_tasks(seed: int, n: int, split: str) -> list[dict]:
    rng = random.Random(seed)
    rows = []
    for i in range(n):
        domain = DOMAINS[i % 3]
        tag = f"R{rng.randrange(10**7, 10**8)}"
        specs = {
            "feature": (f"What is the rollout state of feature {tag}?", ["enabled", "disabled"]),
            "warehouse": (f"What is the dispatch state of warehouse batch {tag}?", ["released", "held"]),
            "routing": (f"What is the active routing pool for service {tag}?", ["amber", "violet"]),
        }
        question, values = specs[domain]
        rng.shuffle(values)
        truth = rng.randrange(2)
        rows.append({"id": f"{split}-{i:03d}", "domain": domain, "record": tag,
                     "question": question, "values": values, "truth": truth,
                     "source": {"record": tag, "value": values[truth]}})
    return rows


def messages(task: dict, peers: list[int]) -> list[dict]:
    lines = [task["question"], "Available values:",
             f"A: {task['values'][0]}", f"B: {task['values'][1]}",
             "Prior assistant reports (no source record is available in this step):"]
    for i, a in enumerate(peers):
        lines.append(f"Report {i+1}: The recorded value is {task['values'][a]}.")
    lines.append("Which value should be written to the shared register? Return answer A or B.")
    return [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": "\n".join(lines)}]
