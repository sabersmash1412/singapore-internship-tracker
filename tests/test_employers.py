import json
import unittest
from urllib.parse import parse_qs, urlsplit

from tracker.sources import fetch
from tracker.classify import eligible


class EmployerTests(unittest.TestCase):
    def test_specific_hardware_internships(self):
        for title in ['Advanced Packaging Optical Characterization Intern', 'Diagnostic Design Engineering Intern',
                      'IC Design Exploration Intern', 'Next-Gen Server Test & Qualification Intern']:
            self.assertTrue(eligible(dict(title=title, location='Singapore')))
        self.assertFalse(eligible(dict(title='Packaging Operations Intern', location='Singapore')))

    def test_team_names_do_not_make_logistics_roles_technical(self):
        for title in ['Transportation Management Intern, AWS Cloud Logistics',
                      'Program Manager Intern, AWS Cloud Logistics', 'DC Security Specialist Intern, DC Security']:
            self.assertFalse(eligible(dict(title=title, location='Singapore')))
        self.assertTrue(eligible(dict(title='Software Intern, AWS Cloud Logistics', location='Singapore')))

    def company(self, platform):
        return dict(name=platform, platform=platform, slug=platform,
                    api_base='https://example.com/api', careers_url='https://example.com/search?location=Singapore')

    def amazon_row(self, identifier, country='SGP'):
        return dict(id_icims=identifier, title='Software Intern', location='Office',
                    country_code=country, job_path='/en/jobs/' + identifier,
                    description='Internship starting January 2027.', posted_date='September 24, 2026',
                    locations=[])

    def test_amazon_paginates_and_filters_by_posting_country(self):
        offsets = []
        def get(url):
            offset = int(parse_qs(urlsplit(url).query)['offset'][0])
            offsets.append(offset)
            return dict(hits=2, jobs=[self.amazon_row(str(offset), 'SGP' if offset else 'USA')])
        result = fetch(self.company('amazon'), get=get)
        self.assertTrue(result.complete)
        self.assertEqual(offsets, [0, 1])
        self.assertEqual([eligible(r) for r in result.jobs], [False, True])
        self.assertEqual(result.jobs[0]['posted_at'], '2026-09-24')

    def test_amazon_secondary_singapore_location(self):
        row = self.amazon_row('1', 'USA')
        row['locations'] = [json.dumps(dict(city='Singapore', normalizedCountryName='Singapore'))]
        result = fetch(self.company('amazon'), get=lambda _:dict(hits=1, jobs=[row]))
        self.assertTrue(result.complete)
        self.assertTrue(eligible(result.jobs[0]))

    def test_repeated_and_changing_pages_fail_closed(self):
        for changing in [False, True]:
            def get(url):
                offset = int(parse_qs(urlsplit(url).query)['offset'][0])
                return dict(hits=3 if changing and offset else 2, jobs=[self.amazon_row('1')])
            self.assertFalse(fetch(self.company('amazon'), get=get).complete)

    def test_amd_nested_payload_and_missing_total(self):
        row = dict(slug='1', title='Hardware Intern', full_location='Singapore',
                   country='Singapore', description='Internship', posted_date='2026-09-24')
        result = fetch(self.company('amd'), get=lambda _:dict(totalCount=1, jobs=[dict(data=row)]))
        self.assertTrue(result.complete)
        self.assertTrue(eligible(result.jobs[0]))
        self.assertFalse(fetch(self.company('amd'), get=lambda _:dict(jobs=[])).complete)

    def html(self, section, data):
        return 'window.__staticRouterHydrationData = JSON.parse(' + json.dumps(json.dumps(dict(loaderData={section:data}))) + ');'

    def test_apple_detail_and_identity_guard(self):
        row = dict(id='1-2', postingTitle='Security Intern', locations=[dict(name='Singapore')], transformedPostingTitle='security-intern')
        for identifier in ['1-2', 'wrong']:
            def text(url):
                if '/details/' in url:
                    return self.html('jobDetails', dict(jobsData=dict(jobNumber=identifier, postingTitle='Security Intern',
                        locations=row['locations'], description='Internship starting January 2027.', postingDateMeta='2026-09-24')))
                return self.html('search', dict(totalRecords=1, searchResults=[row]))
            result = fetch(self.company('apple'), text=text)
            self.assertEqual(result.complete, identifier == '1-2')
            if result.complete:
                self.assertTrue(eligible(result.jobs[0]))
                self.assertIn('January 2027', result.jobs[0]['description'])
        self.assertFalse(fetch(self.company('apple'), text=lambda _:'Service unavailable').complete)

    def test_workday_resolves_all_singapore_sites(self):
        company = self.company('workday')
        company['location_facet'] = 'locations'
        calls = []
        def post(url, body):
            calls.append(body)
            if not body['searchText']:
                return dict(facets=[dict(facetParameter='group', values=[dict(facetParameter='locations', values=[
                    dict(id='a', descriptor='Fab 10A, Singapore'), dict(id='b', descriptor='MSB, Singapore'),
                    dict(id='c', descriptor='Penang, Malaysia')])])])
            return dict(total=0, jobPostings=[])
        self.assertTrue(fetch(company, post=post).complete)
        self.assertEqual(calls[1]['appliedFacets'], {'locations':['a','b']})
        self.assertFalse(fetch(company, post=lambda *args:dict(facets=[])).complete)


if __name__ == '__main__':
    unittest.main()
