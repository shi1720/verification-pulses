import argparse
import asyncio
import json
import random
from pathlib import Path
from verification_pulses.api import Recorder
from verification_pulses.tasks import make_tasks, messages

MODELS = ["gpt-4.1-mini-2025-04-14", "gpt-4.1-nano-2025-04-14"]


async def main(args):
    split = "pilot" if args.pilot else "calibration"
    tasks = make_tasks(91824 if args.pilot else 227641, 12 if args.pilot else 96, split)
    Path(f"data/{split}_tasks.json").write_text(json.dumps(tasks, indent=2) + "\n")
    recorder = Recorder(Path(f"data/raw/{split}.jsonl"), args.key_file, args.concurrency)
    jobs = []
    for t in tasks:
        for k in range(4):
            peers = [1-t["truth"]]*k + [t["truth"]]*(3-k)
            random.Random(f"{split}:{t['id']}:{k}").shuffle(peers)
            for model in MODELS:
                rid = f"{split}:{model}:{t['id']}:{k}"
                jobs.append((rid, model, messages(t, peers), {"task_id": t["id"], "wrong_peers": k, "truth": t["truth"], "domain": t["domain"]}))
    random.Random(551).shuffle(jobs)
    if args.limit:
        jobs = jobs[:args.limit]
    rows = await asyncio.gather(*(recorder.call(*job) for job in jobs))
    await recorder.close()
    for model in MODELS:
        for k in range(4):
            subset = [r for r in rows if r["request"]["model"] == model and r["metadata"]["wrong_peers"] == k]
            valid = [r for r in subset if r.get("answer") is not None]
            wrong = sum(r["answer"] != r["metadata"]["truth"] for r in valid)
            print(model, k, "wrong", wrong, "valid", len(valid), "total", len(subset))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--pilot", action="store_true")
    p.add_argument("--limit", type=int)
    p.add_argument("--key-file")
    p.add_argument("--concurrency", type=int, default=8)
    asyncio.run(main(p.parse_args()))
