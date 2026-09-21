#!/usr/bin/env python3
"""Usage: python3 run.py update | render | serve [--port 8000]."""
import argparse
import functools
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from tracker import sources, state
from tracker.publish import publish

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["update", "render", "serve"])
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if args.command == "serve":
        print(f"Dashboard: http://localhost:{args.port}", flush=True)
        handler = functools.partial(SimpleHTTPRequestHandler, directory=str(ROOT / "docs"))
        ThreadingHTTPServer(("127.0.0.1", args.port), handler).serve_forever()
        return
    current = state.load(ROOT / "data/state.json")
    if args.command == "update":
        companies = json.loads((ROOT / "data/companies.json").read_text())
        if not isinstance(companies, list) or not companies:
            raise ValueError("Company registry must be a non-empty list")
        keys = [f"{c['platform']}:{c['slug']}" for c in companies]
        if len(set(keys)) != len(keys):
            raise ValueError("Duplicate company boards")
        with ThreadPoolExecutor(max_workers=4) as executor:
            snapshots = list(executor.map(sources.fetch, companies))
        for snapshot in snapshots:
            print(f"{snapshot.board}: {len(snapshot.jobs)} jobs, complete={snapshot.complete}, error={snapshot.error}")
        if not any(s.complete for s in snapshots):
            raise SystemExit("All sources failed or were incomplete. Previous data and site preserved.")
        current = state.merge(current, snapshots, datetime.now(timezone.utc).isoformat())
        # Generate artifacts before committing state. CI publishes only on success.
        publish(ROOT, current)
        state.write_json(ROOT / "data/state.json", current)
    else:
        publish(ROOT, current)
    print(f"Published {sum(j['is_open'] for j in current['jobs'].values())} open internships to docs/")


if __name__ == "__main__":
    main()
