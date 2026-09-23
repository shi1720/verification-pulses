"""Minimal append-only API runner. Never writes authentication headers."""
from __future__ import annotations
import asyncio
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
import httpx


class Recorder:
    def __init__(self, path: Path, key_file: str | None = None, concurrency: int = 8):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.key = os.environ.get("OPENAI_API_KEY")
        if not self.key and key_file:
            self.key = Path(key_file).read_text().strip()
        if not self.key:
            raise RuntimeError("Set OPENAI_API_KEY or provide --key-file outside the repository")
        self.saved = {}
        if path.exists():
            for line in path.read_text().splitlines():
                r = json.loads(line)
                if r.get("terminal"):
                    self.saved[r["request_id"]] = r
        self.sem = asyncio.Semaphore(concurrency)
        self.client = httpx.AsyncClient(timeout=90)
        self.calls = len(self.saved)
        self.tokens = 0

    async def close(self):
        await self.client.aclose()

    def append(self, r):
        with self.path.open("a") as f:
            f.write(json.dumps(r, sort_keys=True) + "\n")

    async def call(self, rid: str, model: str, messages: list, metadata: dict):
        if rid in self.saved:
            return self.saved[rid]
        payload = {
            "model": model, "messages": messages, "temperature": 0.7,
            "max_completion_tokens": 40, "store": False,
            "response_format": {"type": "json_schema", "json_schema": {
                "name": "register_answer", "strict": True, "schema": {
                    "type": "object", "properties": {"answer": {"type": "string", "enum": ["A", "B"]}},
                    "required": ["answer"], "additionalProperties": False}}}}
        sha = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        async with self.sem:
            for attempt in range(3):
                row = {"request_id": rid, "request_sha256": sha, "request": payload,
                       "metadata": metadata, "attempt": attempt,
                       "started_utc": datetime.now(timezone.utc).isoformat()}
                start = time.monotonic()
                try:
                    resp = await self.client.post("https://api.openai.com/v1/chat/completions",
                        headers={"Authorization": "Bearer " + self.key}, json=payload)
                    row["http_status"] = resp.status_code
                    body = resp.json()
                    row["response"] = body
                    if resp.status_code != 200:
                        row["error"] = body.get("error", {}).get("code", "http_error")
                        retry = resp.status_code in (429, 500, 502, 503, 504)
                        row["terminal"] = not retry or attempt == 2
                    else:
                        row["terminal"] = True
                        row["answer"] = None
                        try:
                            choice = body["choices"][0]
                            obj = json.loads(choice["message"]["content"])
                            if choice["finish_reason"] == "stop" and obj in ({"answer": "A"}, {"answer": "B"}):
                                row["answer"] = int(obj["answer"] == "B")
                        except (KeyError, TypeError, ValueError, IndexError):
                            pass
                except (httpx.HTTPError, ValueError) as e:
                    row["error"] = type(e).__name__
                    row["terminal"] = attempt == 2
                row["elapsed_s"] = time.monotonic() - start
                self.append(row)
                if row["terminal"]:
                    self.saved[rid] = row
                    self.calls += 1
                    if self.calls % 100 == 0:
                        print(f"completed requests: {self.calls}", flush=True)
                    return row
                await asyncio.sleep(2 ** attempt)
        raise RuntimeError("unreachable")
