import unittest
import json
import tempfile
from pathlib import Path

from tracker.publish import publish
from tracker.state import merge
from tracker.sources import Snapshot
from datetime import date

from tracker.classify import category
from tracker.periods import older_period


class PeriodTests(unittest.TestCase):
    def test_elapsed_current_year_periods(self):
        today = date(2026, 9, 24)
        for value in ['January - May 2026', 'H1 2026', 'Spring 2026', 'Summer 2026', '2025 Start']:
            self.assertTrue(older_period(value, today), value)
        for value in [None, 'Fall 2026', 'H2 2026', '2026 Start', 'Winter 2026', 'Spring 2027']:
            self.assertFalse(older_period(value, today), value)

    def test_mixed_periods_and_unknown_are_not_hidden(self):
        for value in ['Fall 2025 / Spring 2027', 'H1 2026 / Unconfirmed', 'Jan 2027 - May 2026']:
            self.assertFalse(older_period(value, date(2026, 9, 24)))
        self.assertTrue(older_period('Spring 2025 / Summer 2026', date(2026, 9, 24)))

    def test_boundary_and_cross_year(self):
        self.assertFalse(older_period('Jan - Jun 2026', date(2026, 6, 30)))
        self.assertTrue(older_period('Jan - Jun 2026', date(2026, 7, 1)))
        self.assertFalse(older_period('Dec 2026 - Feb 2027', date(2027, 2, 28)))
        self.assertTrue(older_period('Dec 2026 - Feb 2027', date(2027, 3, 1)))

    def test_administrative_team_names_do_not_qualify(self):
        for title in ['HR Business Partner, Project Intern (Data)',
                      'Data Center Business Development and Commercial Intern',
                      'Project Management Project Intern (AI Data (Eco Governance))',
                      'Project Management Project Intern （ AI Data (Safety Model Operations) ）']:
            self.assertIsNone(category(title), title)
        for title in ['IT Project Management Intern', 'Workflow Automation Intern - People Team',
                      'SPX Express Business Development Intern - Data Analytics',
                      'Security & Threat Management Project Intern']:
            self.assertIsNotNone(category(title), title)

    def test_older_rows_move_without_closing_or_losing_exports(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'README.md').write_text('<!-- INTERNSHIPS:START -->\n<!-- INTERNSHIPS:END -->')
            empty = dict(schema_version=1, jobs={}, sources=[], last_attempt_at=None)
            jobs = [dict(id=str(i), board='test', company='Test', title=title,
                         location='Singapore', url=f'https://example.com/{i}', posted_at=None)
                    for i, title in enumerate(['Software Intern Summer 2026', 'Software Intern Fall 2026 / Spring 2027'])]
            state = merge(empty, [Snapshot('test', jobs, True)], '2026-09-24T00:00:00+00:00')
            publish(root, state)
            readme = (root / 'README.md').read_text()
            self.assertIn('1 current or undated listings · 1 older advertised periods', readme)
            before, after = readme.split('<summary>Older advertised periods', 1)
            self.assertNotIn('Software Intern Summer 2026', before)
            self.assertIn('Software Intern Summer 2026', after)
            self.assertIn('Software Intern Fall 2026 / Spring 2027', before)
            exported = json.loads((root / 'data/jobs.json').read_text())['jobs']
            self.assertEqual(len(exported), 2)
            self.assertTrue(all(j['is_open'] for j in exported))
