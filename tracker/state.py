"""Persistent lifecycle. Two complete misses close a listing; errors reset misses."""
import copy
import json
import os
from pathlib import Path

from .classify import eligible, enrich
from .deadlines import deadline_passed


def load(path):
    if not path.exists():
        return {"schema_version": 1, "jobs": {}, "last_attempt_at": None, "sources": []}
    data = json.loads(path.read_text())
    if not isinstance(data, dict) or data.get("schema_version") != 1 or not isinstance(data.get("jobs"), dict):
        raise ValueError("Invalid state; refusing to overwrite job history")
    for identifier, job in data["jobs"].items():
        if not isinstance(job, dict) or job.get("id") != identifier or not all(job.get(k) for k in ("board", "title", "company", "url", "first_seen_at", "last_seen_at")) or type(job.get("is_open")) is not bool:
            raise ValueError(f"Invalid stored job: {identifier}")
    return data


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w") as output:
        json.dump(data, output, ensure_ascii=False, indent=2, sort_keys=True)
        output.write("\n")
        output.flush()
        os.fsync(output.fileno())
    temporary.replace(path)


def merge(previous, snapshots, now):
    state = copy.deepcopy(previous)
    jobs = state["jobs"]
    reports = []
    for snapshot in snapshots:
        selected = [enrich(dict(job)) for job in snapshot.jobs if eligible(job)]
        seen = {job["id"] for job in snapshot.jobs}
        for job in selected:
            old = jobs.get(job["id"], {})
            retained = ["posted_at"]
            if job.pop("detail_unavailable", False):
                retained += ["period", "period_evidence", "duration", "duration_evidence"]
            for key in retained:
                if job.get(key) is None and old.get(key):
                    job[key] = old[key]
            jobs[job["id"]] = {
                **job, "first_seen_at": old.get("first_seen_at", now),
                "last_seen_at": now, "is_open": True, "closed_at": None, "missing_runs": 0,
            }
        selected_ids = {j["id"] for j in selected}
        for identifier, job in jobs.items():
            if job["board"] != snapshot.board or not job["is_open"] or identifier in selected_ids:
                continue
            if identifier in seen:
                # The employer returned it, but it no longer matches our scope.
                # This is positive evidence, not an absence needing two checks.
                job["last_seen_at"] = now
                job["is_open"], job["closed_at"] = False, now
                continue
            if not snapshot.complete:
                job["missing_runs"] = 0
                continue
            # A returned role that no longer matches scope is withdrawn too.
            job["missing_runs"] = job.get("missing_runs", 0) + 1
            if identifier in seen:
                job["last_seen_at"] = now
            if job["missing_runs"] >= 2:
                job["is_open"], job["closed_at"] = False, now
        reports.append(dict(board=snapshot.board, complete=snapshot.complete,
                            fetched=len(snapshot.jobs), matched=len(selected),
                            error=snapshot.error, warnings=snapshot.warnings))
    # Retained listings must expire even when their source is unavailable.
    for identifier, job in jobs.items():
        if job['is_open'] and deadline_passed(job, now):
            old = previous['jobs'].get(identifier, {})
            same_closure = (old.get('closed_reason') == 'Application deadline passed'
                            and old.get('application_deadline_at') == job['application_deadline_at'])
            job.update(is_open=False, closed_reason='Application deadline passed',
                       closed_at=old['closed_at'] if same_closure else now)
    state.update(last_attempt_at=now, sources=reports)
    return state
