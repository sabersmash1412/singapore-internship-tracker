import unittest
from tracker.sources import fetch
from tracker.classify import eligible, extract_period


class ExpansionTests(unittest.TestCase):
    ashby = dict(name='Example', platform='ashby', slug='example')

    def posting(self, **changes):
        return dict(id='p1', title='Software Engineer', location='Singapore',
                    address={'postalAddress': {'addressCountry': 'SG'}},
                    isListed=True, employmentType='Intern', jobUrl='https://example.com/job/1',
                    descriptionPlain='Build software', publishedAt='2026-09-24', **changes)

    def test_structured_internship_and_public_visibility(self):
        row = self.posting()
        result = fetch(self.ashby, get=lambda _: {'apiVersion':'1', 'jobs':[row]})
        self.assertTrue(result.complete)
        self.assertTrue(eligible(result.jobs[0]))
        row['isListed'] = False
        self.assertEqual(fetch(self.ashby, get=lambda _: {'apiVersion':'1', 'jobs':[row]}).jobs, [])

    def test_secondary_country_is_location_evidence(self):
        row = self.posting()
        row.update(location='New York', address={'postalAddress': {'addressCountry': 'US'}},
                   secondaryLocations=[{'location':'Office', 'address':{'addressCountry':'SG'}}])
        result = fetch(self.ashby, get=lambda _: {'apiVersion':'1', 'jobs':[row]})
        self.assertTrue(result.complete)
        self.assertTrue(eligible(result.jobs[0]))
        row.update(location='Remote APAC', address={}, secondaryLocations=[])
        result = fetch(self.ashby, get=lambda _: {'apiVersion':'1', 'jobs':[row]})
        self.assertFalse(eligible(result.jobs[0]))

    def test_malformed_ashby_is_incomplete(self):
        row = self.posting()
        for payload in [{}, {'apiVersion':'2','jobs':[]}, {'apiVersion':'1','jobs':[row,row]},
                        {'apiVersion':'1','jobs':[{**row,'isListed':None}]},
                        {'apiVersion':'1','jobs':[{**row,'id':None}]},
                        {'apiVersion':'1','jobs':None}]:
            with self.subTest(payload=payload):
                self.assertFalse(fetch(self.ashby, get=lambda _:payload).complete)

    def test_shared_board_retains_agency_and_stable_board_id(self):
        company=dict(name='Public Service',platform='workday',slug='gov',shared_employers=True,
                     api_base='https://example.com/api',careers_url='https://example.com/careers')
        listing={'total':1,'jobPostings':[dict(title='Data Intern',externalPath='/job/Office/Data_JR1')]}
        detail={'hiringOrganization':{'name':'Example Agency'},'jobPostingInfo':dict(
            title='Data Intern',location='Office',country={'descriptor':'Singapore'},jobDescription='Analyze data')}
        result=fetch(company,post=lambda *a:listing,get=lambda _:detail)
        self.assertTrue(result.complete)
        self.assertEqual(result.jobs[0]['company'],'Example Agency')
        self.assertEqual(result.jobs[0]['board'],'workday:gov')
        self.assertTrue(eligible(result.jobs[0]))
        detail.pop('hiringOrganization')
        self.assertFalse(fetch(company,post=lambda *a:listing,get=lambda _:detail).complete)
        self.assertFalse(fetch(company,post=lambda *a:listing,get=lambda _:{}).complete)

    def test_nontechnical_team_names_and_learning_content(self):
        for title in ['People & Culture Intern (AI Central)', 'Learning Developer Intern',
                      'Business & Strategy Analyst Intern (AI and Smart Systems)',
                      'AI Strategy & Planning Intern']:
            self.assertFalse(eligible(dict(title=title,location='Singapore')), title)
        self.assertTrue(eligible(dict(title='AI Presales & Solution Engineering Intern',location='Singapore')))
        self.assertEqual(extract_period('[Uni - Jan till Jun 2027] Software Engineer Intern','')[0], 'Jan till Jun 2027')
