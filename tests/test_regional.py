import json
import unittest

from tracker.classify import eligible, enrich
from tracker.sources import fetch
from tracker.regional import checked_page


class RegionalTests(unittest.TestCase):
    supplier = dict(name='TikTok', platform='bytedance', slug='tiktok',
                    api_base='https://api.example.com', careers_url='https://example.com/search', website_path='tiktok')
    workday = dict(name='DBS', platform='workday', slug='dbs', api_base='https://example.com/cxs/dbs/jobs', careers_url='https://example.com/careers')
    sea = dict(name='Sea', platform='sea', slug='sea', api_base='https://example.com/api', careers_url='https://example.com/jobs')
    gov = dict(name='GovTech', platform='govtech', slug='internships', careers_url='https://internships.tech.gov.sg/projects')

    def test_supplier_paginates_and_preserves_structured_internship(self):
        calls = []
        def post(url, body, headers):
            if url.endswith('filters'):
                return {'code': 0, 'data': {'city_list': [{'code': 'SG', 'en_name': 'Singapore'}]}}
            calls.append(body)
            identifier = str(body['offset'])
            return {'code': 0, 'data': {'count': 2, 'job_post_list': [dict(id=identifier, title='Software Engineering', city_info={'en_name':'Singapore'}, recruit_type={'en_name':'Intern'}, description='2027 start')]}}
        snapshot = fetch(self.supplier, post=post)
        self.assertTrue(snapshot.complete)
        self.assertEqual([p['offset'] for p in calls], [0, 1])
        self.assertEqual(calls[0]['location_code_list'], ['SG'])
        self.assertTrue(eligible(snapshot.jobs[0]))
        self.assertIsNone(snapshot.jobs[0]['posted_at'])

    def test_supplier_error_is_not_empty_board(self):
        snapshot = fetch(self.supplier, post=lambda *args: {'code': 500, 'data': {}})
        self.assertFalse(snapshot.complete)
        self.assertIsNotNone(snapshot.error)

    def test_page_validation(self):
        for page,total,seen in [([{'id':'1'}],None,set()), ([{'id':'1'}],1,{'1'}), ([],2,{'1'}), ([{'id':'1'},{'id':'1'}],2,set())]:
            with self.assertRaises(ValueError):
                checked_page(page,total,seen,'id')

    def test_workday_detail_resolves_country_and_date(self):
        def post(*args):
            return {'total':1,'jobPostings':[dict(title='Data Intern',externalPath='/job/Office/Data-Intern_JR1',locationsText='Office')]}
        detail={'jobPostingInfo':dict(title='Data Intern',location='Central Region',country={'descriptor':'Singapore'},jobDescription='Internship',startDate='2026-09-23')}
        snapshot=fetch(self.workday,post=post,get=lambda _:detail)
        self.assertTrue(snapshot.complete)
        self.assertTrue(eligible(snapshot.jobs[0]))
        self.assertEqual(snapshot.jobs[0]['posted_at'],'2026-09-23')

    def test_workday_detail_failure_prevents_closure(self):
        def post(*args):
            return {'total':1,'jobPostings':[dict(title='Data Intern',externalPath='/job/Office/Data-Intern_JR1',locationsText='Office')]}
        snapshot=fetch(self.workday,post=post,get=lambda _: {})
        self.assertFalse(snapshot.complete)
        self.assertTrue(snapshot.warnings)
        self.assertTrue(snapshot.jobs[0]['detail_unavailable'])

    def test_workday_zero_later_total_is_not_truncation(self):
        def post(url, body):
            offset = body['offset']
            return {'total': 2 if offset == 0 else 0,
                    'jobPostings': [dict(title='Engineer', externalPath=f'/job/SG/Engineer_{offset}') ]}
        snapshot = fetch(self.workday, post=post)
        self.assertTrue(snapshot.complete)

    def test_multiple_stated_periods_are_preserved(self):
        job = enrich(dict(title='[Fall 2026] Data Analyst Intern (Spring 2027)', description=''))
        self.assertEqual(job['period'], 'Fall 2026 / Spring 2027')

    def test_sea_uses_live_location_metadata(self):
        urls=[]
        def get(url):
            urls.append(url)
            if 'meta/slice' in url:
                return {'code':0,'data':{'flat_locations':[{'city_id':42,'city_name':'Singapore','region_name':'Singapore','region_abbr':'SG'}], 'employment_level_list':[{'employment_level_id':4,'employment_type_name':'Internship'}]}}
            return {'code':0,'data':{'total_count':1,'job_list':[dict(job_id='J123',job_name='Security Engineering',city_id=42,employment_id=4)]}}
        snapshot=fetch(self.sea,get=get)
        self.assertTrue(snapshot.complete)
        self.assertIn('city_ids=42',urls[-1])
        self.assertTrue(eligible(snapshot.jobs[0]))
        self.assertEqual(snapshot.jobs[0]['url'],'https://career.sea.com/position/J123')

    def test_sea_unmapped_city_poison_completeness(self):
        def get(url):
            if 'meta/slice' in url:
                return {'code':0,'data':{'flat_locations':[{'city_id':42,'region_abbr':'SG'}], 'employment_level_list':[{'employment_level_id':4,'employment_type_name':'Internship'}]}}
            return {'code':0,'data':{'total_count':1,'job_list':[dict(job_id='J123',city_id=99)]}}
        self.assertFalse(fetch(self.sea,get=get).complete)

    def gov_html(self, location='Punggol Digital District', filled=False):
        groups={key:[] for key in ['cybersecurity-engineer','data-engineer','data-scientist','software-engineer','systems-engineer']}
        groups['software-engineer']=[dict(id='p1',role='Software Engineer',projectTitle='Build citizen services',projectDescription='$a',filled=filled,workLocation=location,roleSlug='software-engineer',projectSlug='citizen-services',internshipDurations=['6 months'])]
        payload='1:'+json.dumps({'internships':groups})
        return '<script>self.__next_f.push('+json.dumps([1,payload])+')</script>'

    def test_govtech_structured_role_and_duration(self):
        result=fetch(self.gov,text=lambda _:self.gov_html())
        self.assertTrue(result.complete)
        self.assertTrue(eligible(result.jobs[0]))
        enriched=enrich(result.jobs[0])
        self.assertEqual(enriched['duration'],'6 months')
        self.assertEqual(enriched['category'],'Software')

    def test_govtech_filled_and_unknown_location(self):
        self.assertEqual(fetch(self.gov,text=lambda _:self.gov_html(filled=True)).jobs,[])
        result=fetch(self.gov,text=lambda _:self.gov_html(location='Others'))
        self.assertFalse(eligible(result.jobs[0]))
        self.assertFalse(fetch(self.gov,text=lambda _: '<html>Service unavailable</html>').complete)

    def test_structured_employment_does_not_admit_fulltime(self):
        job=dict(title='Software Engineer',location='Singapore',employment_type='Full-time')
        self.assertFalse(eligible(job))
        job = dict(title='Talent Acquisition Project Intern (AI Data Service and Operations)', location='Singapore')
        self.assertFalse(eligible(job))
        job = dict(title='Internship: Global Corporate Banking, Global Energy, Infrastructure & Utilities', location='Singapore')
        self.assertFalse(eligible(job))
        for title in ['Datacenter Operations Engineer Intern (Infrastructure Engineering)', 'Production System Engineer Intern', 'Site Reliability Engineer Intern']:
            self.assertTrue(eligible(dict(title=title, location='Singapore')))


if __name__ == '__main__':
    unittest.main()
