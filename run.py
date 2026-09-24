#!/usr/bin/env python3
"""Usage: python3 run.py update | render | check."""
import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

from tracker import sources, state
from tracker.publish import publish

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["update", "render", "check"])
    args = parser.parse_args()
    current = state.load(ROOT / "data/state.json")
    if args.command == "check":
        from tracker.health import check
        companies = json.loads((ROOT / "data/companies.json").read_text())
        try:
            count = check(current, companies)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        print(f"All {count} employer feeds completed successfully in the saved snapshot.")
        return
    if args.command == "update":
        companies = json.loads((ROOT / "data/companies.json").read_text())
        if not isinstance(companies, list) or not companies:
            raise ValueError("Company registry must be a non-empty list")
        keys = [f"{c['platform']}:{c['slug']}" for c in companies]
        if len(set(keys)) != len(keys):
            raise ValueError("Duplicate company boards")
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(sources.fetch, company): index for index, company in enumerate(companies)}
            completed = {}
            for future in as_completed(futures):
                snapshot = future.result()
                completed[futures[future]] = snapshot
                print(f"{snapshot.board}: {len(snapshot.jobs)} jobs, complete={snapshot.complete}, error={snapshot.error}", flush=True)
            snapshots = [completed[index] for index in range(len(companies))]
        if not any(s.complete for s in snapshots):
            raise SystemExit("All sources failed or were incomplete. Previous README and data preserved.")
        current = state.merge(current, snapshots, datetime.now(timezone.utc).isoformat())
        # Generate artifacts before committing state. CI publishes only on success.
        publish(ROOT, current)
        state.write_json(ROOT / "data/state.json", current)
    else:
        publish(ROOT, current)
    print(f"Published {sum(j['is_open'] for j in current['jobs'].values())} open internships to README.md and data/")


if __name__ == "__main__":
    main()
