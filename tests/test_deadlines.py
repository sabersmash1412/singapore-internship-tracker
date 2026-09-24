import json
import tempfile
import unittest
from pathlib import Path

from tracker.deadlines import govtech_deadline
from tracker.sources import Snapshot, fetch
from tracker.state import merge
from tracker.publish import publish

EMPTY = dict(schema_version=1, jobs={}, sources=[], last_attempt_at=None)
JOB = dict(id='gov:1', board='gov', company='GovTech', title='Software Intern',
           location='Singapore', url='https://example.com/job', posted_at=None,
           application_deadline_at='2026-09-30T12:00:00+08:00', deadline_source='https://example.com/programme')


class DeadlineTests(unittest.TestCase):
    def test_noon_singapore_and_midnight(self):
        self.assertEqual(govtech_deadline('<p>Internship applications are now open until <b>30 September 2026, 12pm</b>.</p>'), JOB['application_deadline_at'])
        self.assertEqual(govtech_deadline('Internship applications are open until 1 October 2026, 12:30am'), '2026-10-01T00:30:00+08:00')

    def test_unknown_invalid_and_ambiguous_fail(self):
        for text in ['Apply soon', 'Internship applications are open until 31 September 2026, 12pm',
                     'Internship applications are open until 30 September 2026, 12pm. Internship applications are open until 1 October 2026, 12pm.']:
            with self.assertRaises(ValueError):
                govtech_deadline(text)

    def test_boundary_and_stable_closure_while_catalogue_still_lists_job(self):
        snapshot = Snapshot('gov', [JOB], True)
        state = merge(EMPTY, [snapshot], '2026-09-30T03:59:59+00:00')
        self.assertTrue(state['jobs']['gov:1']['is_open'])
        state = merge(state, [snapshot], '2026-09-30T04:00:00+00:00')
        self.assertFalse(state['jobs']['gov:1']['is_open'])
        self.assertEqual(state['jobs']['gov:1']['closed_reason'], 'Application deadline passed')
        state = merge(state, [snapshot], '2026-10-01T00:00:00+00:00')
        self.assertEqual(state['jobs']['gov:1']['closed_at'], '2026-09-30T04:00:00+00:00')

    def test_source_failure_does_not_erase_known_deadline(self):
        state = merge(EMPTY, [Snapshot('gov', [JOB], True)], '2026-09-24T00:00:00+00:00')
        state = merge(state, [Snapshot('gov', [], False, 'deadline page unavailable')], '2026-09-30T04:00:00+00:00')
        self.assertFalse(state['jobs']['gov:1']['is_open'])
        self.assertEqual(state['jobs']['gov:1']['application_deadline_at'], JOB['application_deadline_at'])

    def test_explicit_extended_deadline_reopens(self):
        state = merge(EMPTY, [Snapshot('gov', [JOB], True)], '2026-09-30T04:00:00+00:00')
        extended = dict(JOB, application_deadline_at='2026-10-15T12:00:00+08:00')
        state = merge(state, [Snapshot('gov', [extended], True)], '2026-10-01T00:00:00+00:00')
        job = state['jobs']['gov:1']
        self.assertTrue(job['is_open'])
        self.assertIsNone(job['closed_at'])
        self.assertNotIn('closed_reason', job)

    def test_deadline_page_failure_marks_govtech_incomplete(self):
        company = dict(name='GovTech', platform='govtech', slug='internships', careers_url='https://example.com/projects')
        result = fetch(company, text=lambda _: 'Internships available')
        self.assertFalse(result.complete)
        self.assertEqual(result.jobs, [])

    def test_closed_deadline_excluded_from_active_exports(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'README.md').write_text('<!-- INTERNSHIPS:START -->\n<!-- INTERNSHIPS:END -->')
            state = merge(EMPTY, [Snapshot('gov', [JOB], True)], '2026-09-24T00:00:00+00:00')
            publish(root, state)
            self.assertIn('30 Sep 2026, 12:00 SGT', (root/'README.md').read_text())
            state = merge(state, [Snapshot('gov', [JOB], True)], '2026-09-30T04:00:00+00:00')
            publish(root, state)
            self.assertEqual(json.loads((root/'data/jobs.json').read_text())['jobs'], [])
            self.assertIn('Application deadline passed', (root/'README.md').read_text())
            self.assertNotIn('[Apply]', (root/'README.md').read_text())


class CountryFacetTests(unittest.TestCase):
    company = dict(name='Test', platform='workday', slug='test', api_base='https://example.com/api', careers_url='https://example.com/careers', country_facet='Country')

    def test_nested_live_country_mapping_and_empty_filtered_result(self):
        calls = []
        def post(url, body):
            calls.append(body)
            if body['searchText'] == '':
                return {'facets': [{'facetParameter': 'group', 'values': [{'facets': [{'facetParameter': 'Country', 'values': [{'descriptor': 'Singapore', 'id': 'live-id'}]}]}]}]}
            return {'total': 0, 'jobPostings': []}
        result = fetch(self.company, post=post)
        self.assertTrue(result.complete)
        self.assertEqual(calls[1]['appliedFacets'], {'Country': ['live-id']})

    def test_missing_country_mapping_is_incomplete_not_empty(self):
        result = fetch(self.company, post=lambda *args: {'facets': [{'facetParameter': 'Country', 'values': []}]})
        self.assertFalse(result.complete)

    def test_country_facet_nested_directly_in_values(self):
        def post(url, body):
            if body['searchText'] == '':
                return {'facets': [{'facetParameter': 'group', 'values': [{'facetParameter': 'Country', 'values': [{'descriptor': 'Singapore', 'id': 'nested-id'}]}]}]}
            self.assertEqual(body['appliedFacets'], {'Country': ['nested-id']})
            return {'total': 0, 'jobPostings': []}
        self.assertTrue(fetch(self.company, post=post).complete)

    def test_semiconductor_scope_still_requires_technical_title(self):
        from tracker.classify import eligible
        for title in ['College Intern - Hybrid Bonding', 'College Intern - Process Integration', 'Intern - PVD process development', 'Testchip Design Intern', 'Silicon Photonics Intern']:
            self.assertTrue(eligible(dict(title=title, location='Singapore')))
        for title in ['College Intern', 'University Intern - Year 2026', 'Global Supply Chain Internship Program']:
            self.assertFalse(eligible(dict(title=title, location='Singapore')))
