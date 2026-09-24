import unittest
from tracker.classify import eligible, extract_period


class AuditRegressions(unittest.TestCase):
    def test_verified_technical_specialties(self):
        for title in ['Business Intelligence Intern (Spring 2027)',
                      'Business Intelligence (BI) Intern – Cross Border E-commerce (Summer 2026)',
                      'Regional Large Language Model (LLM) Agent & Prompt Engineering Intern (Spring 2027)',
                      'Intern- Silicon Design Validation Engineer']:
            self.assertTrue(eligible(dict(title=title, location='Singapore')), title)

    def test_finance_team_name_does_not_qualify_role(self):
        for title in ['Regional Finance Business Analyst Intern - Regional Business Intelligence & Planning (Spring 2027)',
                      'Regional Financial Planning and Analysis Intern - Regional Business Intelligence and Planning (BI&P)',
                      'Talent Acquisition Intern (LLM Team)']:
            self.assertFalse(eligible(dict(title=title, location='Singapore')), title)

    def test_intake_bullet_survives_graduation_requirement(self):
        text = 'Currently an undergraduate, graduating between Aug 2027 – Dec 2028 - Able to commit to a full-time internship from Jan to Jun 2027 - Interest in data analytics'
        self.assertEqual(extract_period('Program Manager Intern', text)[0], 'Jan to Jun 2027')
        self.assertIsNone(extract_period('Software Intern', 'Graduating between Aug 2027 - Dec 2028')[0])
        self.assertEqual(extract_period('Software Intern', 'Internship period: Jan 2027 - June 2027')[0], 'Jan 2027 - June 2027')

    def test_engineering_specialties_without_generic_product_matching(self):
        for title in ['Product Builder Intern  (Product Engineering)',
                      'Intern- Test Solutions Engineer', 'Intern - Test Solutions Engineering',
                      'Intern - Product Engineering, NAND Validation/Characterization']:
            self.assertTrue(eligible(dict(title=title, location='Singapore')), title)
            self.assertFalse(eligible(dict(title=title, location='Malaysia')), title)
        for title in ['Product Builder Intern (Product Management)', 'Product Builder Intern',
                      'Product Engineering Intern', 'Test Solutions Marketing Intern']:
            self.assertFalse(eligible(dict(title=title, location='Singapore')), title)
