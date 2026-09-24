import copy
import json
import tempfile
import unittest
from pathlib import Path

from tracker.classify import eligible, enrich, singapore
from tracker.sources import Snapshot, fetch
from tracker.state import load, merge, write_json
from tracker.publish import publish

NOW = "2026-09-21T12:00:00+00:00"
JOB = dict(id="greenhouse:test:1", board="greenhouse:test", title="Software Engineer Intern",
           company="Test", location="Singapore", url="https://example.com/jobs/1",
           description="", posted_at=None, source="greenhouse")


class ClassificationTests(unittest.TestCase):
    def test_singapore_and_multi_location(self):
        self.assertTrue(singapore("Singapore; London"))
        self.assertTrue(singapore("One North", "sg"))
        for location in ("Remote", "APAC", "London", "SG team in London"):
            self.assertFalse(singapore(location))

    def test_title_boundaries(self):
        self.assertTrue(eligible(JOB))
        for title in ("Internal Software Auditor", "Marketing Intern", "Software Engineer"):
            self.assertFalse(eligible({**JOB, "title": title}))

    def test_year_is_not_a_season(self):
        job = enrich({**JOB, "title": "Software Engineer Intern 2027"})
        self.assertIsNone(job["period"])
        job = enrich({**JOB, "title": "Software Engineer Intern - 2027 Start"})
        self.assertEqual(job["period"], "2027 Start")

    def test_explicit_period_and_duration(self):
        job = enrich({**JOB, "description": "This internship runs from Jan to Jun 2027. A minimum of 6 months is required."})
        self.assertEqual(job["period"], "Jan to Jun 2027")
        self.assertEqual(job["duration"], "6 months")

    def test_half_year_and_encoded_html(self):
        job = enrich({**JOB, "description": "&lt;p&gt;Open for H1 2027 internship applications.&lt;/p&gt;"})
        self.assertEqual(job["period"], "H1 2027")

    def test_no_period_from_company_history(self):
        job = enrich({**JOB, "description": "Founded in Summer 2027. We offer an internship."})
        self.assertIsNone(job["period"])


class SourceTests(unittest.TestCase):
    company = dict(name="Test", platform="greenhouse", slug="test")
    row = dict(id=1, title="Software Intern", location={"name": "Singapore"}, absolute_url="https://example.com/1", updated_at=NOW)

    def test_updated_is_not_posted(self):
        result = fetch(self.company, lambda _: {"jobs": [self.row]})
        self.assertTrue(result.complete)
        self.assertIsNone(result.jobs[0]["posted_at"])

    def test_empty_valid_vs_malformed(self):
        self.assertTrue(fetch(self.company, lambda _: {"jobs": []}).complete)
        for payload in ({}, {"jobs": [] , "error": "blocked"}, {"jobs": [{}]}, {"jobs": [1]}):
            self.assertFalse(fetch(self.company, lambda _, p=payload: p).complete)

    def test_duplicate_ids_poison_completeness(self):
        self.assertFalse(fetch(self.company, lambda _: {"jobs": [self.row, self.row]}).complete)

    def test_unsafe_url_rejected(self):
        self.assertFalse(fetch(self.company, lambda _: {"jobs": [{**self.row, "absolute_url": "javascript:alert(1)"}]}).complete)

    def test_pagination_and_stall(self):
        company = dict(name="Test", platform="lever", slug="test")
        page = [dict(id=str(n), text="Software Intern", categories={"location": "Singapore"}, hostedUrl=f"https://example.com/{n}") for n in range(100)]
        calls = []
        def get(url):
            calls.append(url)
            return page if len(calls) == 1 else []
        result = fetch(company, get)
        self.assertTrue(result.complete)
        self.assertEqual(len(result.jobs), 100)
        self.assertIn("skip=100", calls[1])
        self.assertFalse(fetch(company, lambda _: page).complete)

    def test_smartrecruiters_truncated(self):
        company = dict(name="Test", platform="smartrecruiters", slug="test")
        result = fetch(company, lambda _: {"totalFound": 200, "content": []})
        self.assertFalse(result.complete)


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.empty = {"schema_version": 1, "jobs": {}, "sources": [], "last_attempt_at": None}
        self.full = Snapshot("greenhouse:test", [copy.deepcopy(JOB)], True)
        self.missing = Snapshot("greenhouse:test", [], True)

    def test_two_misses_close_and_reappearance_reopens(self):
        state = merge(self.empty, [self.full], NOW)
        state = merge(state, [self.missing], NOW)
        self.assertTrue(state["jobs"][JOB["id"]]["is_open"])
        state = merge(state, [self.missing], NOW)
        self.assertFalse(state["jobs"][JOB["id"]]["is_open"])
        state = merge(state, [self.full], "2026-09-22T12:00:00+00:00")
        self.assertTrue(state["jobs"][JOB["id"]]["is_open"])
        self.assertEqual(state["jobs"][JOB["id"]]["first_seen_at"], NOW)

    def test_outage_resets_missing_counter(self):
        state = merge(self.empty, [self.full], NOW)
        state = merge(state, [self.missing], NOW)
        state = merge(state, [Snapshot("greenhouse:test", error="timeout")], NOW)
        state = merge(state, [self.missing], NOW)
        self.assertTrue(state["jobs"][JOB["id"]]["is_open"])

    def test_corrupt_state_is_fatal(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            path.write_text('{"schema_version": 1, "jobs": {"bad": {}}}')
            with self.assertRaises(ValueError):
                load(path)

    def test_removed_period_is_not_kept_forever(self):
        full = Snapshot("greenhouse:test", [{**JOB, "description": "Internship for H1 2027."}], True)
        state = merge(self.empty, [full], NOW)
        self.assertEqual(state["jobs"][JOB["id"]]["period"], "H1 2027")
        state = merge(state, [self.full], NOW)
        self.assertIsNone(state["jobs"][JOB["id"]]["period"])

    def test_atomic_roundtrip_and_no_input_mutation(self):
        state = merge(self.empty, [self.full], NOW)
        self.assertEqual(self.empty["jobs"], {})
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            write_json(path, state)
            self.assertEqual(load(path), state)

    def test_export_escaping_and_consistent_counts(self):
        import shutil
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(Path(__file__).resolve().parents[1] / "web", root / "web")
            dangerous = {**JOB, "title": "Software Intern </script><script>alert(1)</script>", "company": "=BAD()"}
            state = merge(self.empty, [Snapshot("greenhouse:test", [dangerous], True)], NOW)
            publish(root, state)
            payload = json.loads((root / "docs/api/jobs.json").read_text())
            self.assertEqual(len(payload["jobs"]), 1)
            self.assertNotIn("</script><script>alert", (root / "docs/index.html").read_text())
            self.assertIn("'=BAD()", (root / "docs/internships.csv").read_text())
            original = (root / "docs/index.html").read_bytes()
            write_json(root / "state.json", state)
            publish(root, load(root / "state.json"))
            self.assertEqual(original, (root / "docs/index.html").read_bytes())


if __name__ == "__main__":
    unittest.main()
