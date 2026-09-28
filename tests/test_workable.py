import copy
import io
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from tracker.sources import fetch, pace_workable, request
from tracker.classify import eligible, enrich


class WorkableTests(unittest.TestCase):
    company = dict(name='Example', platform='workable', slug='example')

    def row(self):
        return dict(shortcode='A1', title='Software Engineer Intern', city='Singapore',
                    country='Singapore', locations=[], url='https://apply.workable.com/j/A1',
                    description='Internship from Jan to Jun 2027.', employment_type='Internship',
                    published_on='2026-09-28', created_at='2025-01-01')

    def collect(self, jobs, **envelope):
        return fetch(self.company, get=lambda _:dict(name='Example', jobs=jobs, **envelope))

    def test_public_posting_identity_date_and_intake(self):
        result = self.collect([self.row()])
        self.assertTrue(result.complete)
        job = result.jobs[0]
        self.assertEqual(job['id'], 'workable:example:A1')
        self.assertEqual(job['posted_at'], '2026-09-28')
        self.assertEqual(enrich(job)['period'], 'Jan to Jun 2027')

    def test_secondary_location_and_structured_internship(self):
        row = self.row()
        row.update(title='Software Engineer', city='London', country='UK',
                   locations=[dict(city='Office',countryCode='SG',hidden=False)])
        self.assertTrue(eligible(self.collect([row]).jobs[0]))
        row['locations'][0]['hidden'] = True
        self.assertFalse(eligible(self.collect([row]).jobs[0]))
        row.update(city='Remote APAC',country=None,locations=[])
        self.assertFalse(eligible(self.collect([row]).jobs[0]))

    def test_invalid_snapshot_cannot_be_used_for_closures(self):
        for change in [dict(shortcode=None),dict(title=None),dict(url='http://example.com'),
                       dict(description=None),dict(locations={}),dict(city=None,country=None)]:
            row = self.row();row.update(change)
            self.assertFalse(self.collect([row]).complete,change)
        row = self.row()
        self.assertFalse(self.collect([row,{**row,'title':'Different Intern'}]).complete)
        self.assertFalse(self.collect([row],error='Unavailable').complete)
        self.assertFalse(fetch(self.company,get=lambda _:dict(jobs=[])).complete)

    def test_empty_board_is_valid_with_employer_identity(self):
        result=self.collect([])
        self.assertTrue(result.complete)
        self.assertEqual(result.jobs,[])

    def test_widget_location_variants_merge_to_one_listing(self):
        sg = self.row()
        overseas = {**sg, 'city':'Kuala Lumpur', 'country':'Malaysia'}
        result = self.collect([overseas, sg, copy.deepcopy(sg)])
        self.assertTrue(result.complete)
        self.assertEqual(len(result.jobs),1)
        self.assertTrue(eligible(result.jobs[0]))
        self.assertIn('Kuala Lumpur',result.jobs[0]['location'])
        sg.update(city='Office', country='SG')
        self.assertTrue(eligible(self.collect([overseas, sg]).jobs[0]))

    def test_description_failure_preserves_partial_results(self):
        row=self.row();bad={**row,'shortcode':'A2','description':''}
        result=self.collect([row,bad])
        self.assertFalse(result.complete)
        self.assertEqual(len(result.jobs),1)

    def test_shared_host_pacing_does_not_delay_other_providers(self):
        with patch('tracker.sources.time.sleep') as sleep, patch('tracker.sources.time.monotonic',return_value=100), patch('tracker.sources._workable_next_request',101):
            pace_workable('https://apply.workable.com/api/v1/widget/accounts/example')
            sleep.assert_called_once_with(1)
            sleep.reset_mock()
            pace_workable('https://boards-api.greenhouse.io/v1/boards/example/jobs')
            sleep.assert_not_called()

    def test_workable_rate_limit_gets_cooldown_before_retry(self):
        url='https://apply.workable.com/api/v1/widget/accounts/example'
        error=HTTPError(url,429,'Rate limited',{'Retry-After':'45'},None)
        with patch('tracker.sources.pace_workable'), patch('tracker.sources.time.sleep') as sleep, patch(
                'tracker.sources.urlopen',side_effect=[error,io.StringIO('{"ok":true}')]):
            self.assertEqual(request(url),{'ok':True})
            sleep.assert_called_once_with(45)

    def test_non_it_security_and_quality_are_excluded(self):
        for title in ['Intern, Global Security Operations','Quality System Management Intern']:
            self.assertFalse(eligible(dict(title=title,location='Singapore')))
        for title in ['Cybersecurity Operations Intern','IT Quality Systems Management Intern']:
            self.assertTrue(eligible(dict(title=title,location='Singapore')))
