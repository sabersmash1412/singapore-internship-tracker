import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import run
from tracker.health import check


class HealthTests(unittest.TestCase):
    companies = [dict(platform='workday', slug='a'), dict(platform='lever', slug='b')]

    def snapshot(self):
        return dict(schema_version=1, jobs={}, sources=[
            dict(board='workday:a', complete=True, error=None, warnings=[], matched=0),
            dict(board='lever:b', complete=True, error=None, warnings=[], matched=2)])

    def test_zero_matching_jobs_are_healthy(self):
        self.assertEqual(check(self.snapshot(), self.companies), 2)

    def test_partial_outage_and_detail_warnings_fail(self):
        for change in [dict(complete=False), dict(error='Feed error'), dict(warnings=['Detail unavailable'])]:
            snapshot = self.snapshot()
            snapshot['sources'][0].update(change)
            with self.assertRaisesRegex(ValueError, 'workday:a'):
                check(snapshot, self.companies)

    def test_missing_duplicate_or_unexpected_reports_fail(self):
        for boards in [[], ['workday:a'], ['workday:a', 'workday:a'], ['workday:a', 'lever:c']]:
            with self.assertRaises(ValueError):
                check(dict(sources=[dict(board=b, complete=True) for b in boards]), self.companies)

    def test_cli_failure_preserves_published_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'data').mkdir()
            snapshot = self.snapshot()
            snapshot['sources'][0]['complete'] = False
            (root / 'data/state.json').write_text(json.dumps(snapshot))
            (root / 'data/companies.json').write_text(json.dumps(self.companies))
            (root / 'README.md').write_text('Previously published updates')
            (root / 'data/jobs.json').write_text('Export must stay untouched')
            before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
            with patch.object(run, 'ROOT', root), patch('sys.argv', ['run.py', 'check']):
                with self.assertRaises(SystemExit):
                    run.main()
            self.assertEqual(before, {p: p.read_bytes() for p in root.rglob('*') if p.is_file()})
            snapshot['sources'][0]['complete'] = True
            (root / 'data/state.json').write_text(json.dumps(snapshot))
            with patch.object(run, 'ROOT', root), patch('sys.argv', ['run.py', 'check']), contextlib.redirect_stdout(io.StringIO()) as output:
                run.main()
            self.assertIn('All 2 employer feeds', output.getvalue())
