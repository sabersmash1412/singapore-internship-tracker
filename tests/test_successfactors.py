import unittest
from urllib.parse import parse_qs, urlsplit
from tracker.sources import fetch
from tracker.successfactors import search_page
from tracker.classify import eligible


class SuccessFactorsTests(unittest.TestCase):
    company=dict(name='Example',platform='successfactors',slug='example',careers_url='https://example.com')

    def row(self, number=1, title='Software Intern', location='Singapore, SG', department='Example'):
        return f'''<tr class="data-row"><td class="colTitle"><a class="jobTitle-link" href="/job/Role/{number}/">{title}</a><a class="jobTitle-link" href="/job/Role/{number}/">{title}</a></td><td class="colLocation">{location}</td><td class="colDepartment">{department}</td></tr>'''

    def page(self,number=1,total=1,**kwargs):
        return f'Results <b>{number} – {number}</b> of <b>{total}</b><table>{self.row(number,**kwargs)}</table>'

    def detail(self,title='Software Intern'):
        return f'''<h1 itemprop="title">{title}</h1><meta itemprop="datePosted" content="Mon Sep 28 01:00:00 UTC 2026"><span class="jobdescription">Internship <b>Jan to Jun 2027</b></span>'''

    def test_complete_pagination_and_microdata(self):
        seen=[]
        def text(url):
            seen.append(url)
            if '/job/' in url:return self.detail()
            offset=int(parse_qs(urlsplit(url).query)['startrow'][0])
            return self.page(offset+1,total=2)
        result=fetch(self.company,text=text)
        self.assertTrue(result.complete)
        self.assertEqual(len(result.jobs),2)
        self.assertEqual(result.jobs[0]['posted_at'],'2026-09-28T01:00:00+00:00')
        self.assertEqual(result.jobs[0]['description'],'Internship Jan to Jun 2027')
        self.assertTrue(eligible(result.jobs[0]))
        self.assertTrue(any('startrow=1' in u for u in seen))

    def test_explicit_empty_ignores_unrelated_suggestions(self):
        html='<div id="noresults">There are currently no open positions matching this search.</div>'+self.page()
        self.assertEqual(search_page(html),(0,0,0,[]))
        result=fetch(self.company,text=lambda _:html)
        self.assertTrue(result.complete)
        self.assertEqual(result.jobs,[])

    def test_missing_counts_are_incomplete(self):
        self.assertFalse(fetch(self.company,text=lambda _:self.row()).complete)
        self.assertFalse(fetch(self.company,text=lambda _:'Maintenance').complete)

    def test_duplicate_ids_and_total_changes_are_incomplete(self):
        for second in [self.page(2,total=2).replace('/2/','/1/'),self.page(2,total=3),'<div id="noresults">There are currently no open positions matching</div>']:
            def text(url):
                if '/job/' in url:return self.detail()
                return self.page(1,total=2) if 'startrow=0' in url else second
            self.assertFalse(fetch(self.company,text=text).complete)

    def test_count_mismatch_and_ambiguous_links(self):
        with self.assertRaises(ValueError):search_page(self.page().replace('1 – 1','1 – 2'))
        with self.assertRaises(ValueError):search_page(self.page().replace('href="/job/Role/1/"','href="/job/Other/2/"',1))

    def test_shared_board_excludes_other_employer(self):
        c={**self.company,'departments':['Example']}
        result=fetch(c,text=lambda _:self.page(department='Other Employer'))
        self.assertTrue(result.complete)
        self.assertEqual(result.jobs,[])
        self.assertFalse(fetch(c,text=lambda _:self.page(department='')).complete)

    def test_country_code_is_read_from_location_not_description(self):
        for location,expected in [('ST Engineering Hub, SG',True),('SG, 238891',True),('New York, US',False),('SG Team, London',False)]:
            result=fetch(self.company,text=lambda u:self.detail() if '/job/' in u else self.page(location=location))
            self.assertTrue(result.complete)
            self.assertEqual(bool(eligible(result.jobs[0])),expected)

    def test_wrong_detail_and_external_job_link_are_incomplete(self):
        result=fetch(self.company,text=lambda u:self.detail('Another Intern') if '/job/' in u else self.page())
        self.assertFalse(result.complete)
        result=fetch(self.company,text=lambda _:self.page().replace('href="/job/','href="https://other.example/job/'))
        self.assertFalse(result.complete)

    def test_employer_branding_in_ai_team_is_not_technical(self):
        self.assertFalse(eligible(dict(title='Employer Branding & AI Community Intern',location='Singapore')))
