import unittest
from datetime import date

from tracker.classify import enrich
from tracker.periods import older_period


class IntakeTests(unittest.TestCase):
    def parse(self, title='Software Intern', description=''):
        return enrich(dict(title=title, description=description))

    def test_single_month_in_title_is_explicitly_a_start(self):
        job = self.parse('Software Intern (January 2027)')
        self.assertEqual(job['period'], 'January 2027 Start')
        self.assertEqual(job['period_evidence'], 'Software Intern (January 2027)')
        self.assertEqual(self.parse('Software Intern January 2027 Intake')['period'], 'January 2027 Intake')

    def test_half_year_aliases_and_multiple_intakes(self):
        self.assertEqual(self.parse('Software Internship 1H 2027')['period'], 'H1 2027')
        self.assertEqual(self.parse('Software Internship 2H 2026 / 1H 2027')['period'], 'H2 2026 / H1 2027')
        self.assertIsNone(self.parse('2H University Intern - AI')['period'])

    def test_single_month_in_description_requires_context(self):
        for description in ['Available for a minimum commitment of 6 months starting Jan 2027.',
                            'The internship commences in Jan 2027.',
                            'Availability: Jan 2027.', 'Start date: Jan 2027.']:
            self.assertEqual(self.parse(description=description)['period'], 'Jan 2027 Start', description)
        self.assertIsNone(self.parse(description='Our office opened in Jan 2027.')['period'])

    def test_deadline_and_graduation_dates_are_not_intakes(self):
        for description in ['Internship applications close in January 2027.',
                            'Internship application deadline: January 2027.',
                            'Interns must graduate in January 2027.',
                            'Interns: apply by January 2027.',
                            'Our internship programme was established in Summer 2025.']:
            self.assertIsNone(self.parse(description=description)['period'], description)
        self.assertIsNone(self.parse('Software Intern (Graduating January 2027)')['period'])

    def test_later_intake_sentence_survives_eligibility_sentence(self):
        job = self.parse(description='Applicants must graduate in May 2028. Internship starts in January 2027.')
        self.assertEqual(job['period'], 'January 2027 Start')
        self.assertEqual(job['period_evidence'], 'Internship starts in January 2027.')

    def test_ranges_stay_intact_and_title_remains_authoritative(self):
        self.assertEqual(self.parse('Software Intern (Jan-Jun 2027)')['period'], 'Jan-Jun 2027')
        self.assertEqual(self.parse('Software Intern 2027 Start', 'Internship starts January 2027.')['period'], '2027 Start')
        self.assertEqual(self.parse(description='Internship runs from December 2026 to June 2027.')['period'], 'December 2026 to June 2027')

    def test_start_month_does_not_become_a_closing_date(self):
        self.assertFalse(older_period('January 2027 Start', date(2027, 2, 1)))
        self.assertTrue(older_period('January 2027 Start', date(2028, 1, 1)))

    def test_range_end_and_alternative_months_are_not_start_dates(self):
        job = self.parse(description='We accept internship applications for H1 2027 (Dec 2026/Jan 2027 to May/June 2027).')
        self.assertEqual(job['period'], 'H1 2027')
        self.assertIsNone(self.parse(description='The internship runs Dec 2026/Jan 2027 to May/June 2027.')['period'])
        self.assertIsNone(self.parse(description='This internship ends in June 2027.')['period'])
        self.assertIsNone(self.parse(description='The internship end date: June 2027.')['period'])
        self.assertEqual(self.parse(description='The internship starts January 2027 and ends June 2027.')['period'], 'January 2027 Start')

    def test_season_and_single_month_alternatives_both_survive(self):
        self.assertEqual(self.parse('Software Intern Summer 2026 / January 2027')['period'],
                         'Summer 2026 / January 2027 Start')
