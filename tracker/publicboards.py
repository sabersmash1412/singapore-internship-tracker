"""Public job-board formats used by smaller employers."""
from urllib.parse import quote, urlsplit

from .classify import singapore
from .regional import record
from .sources import rows


def workable(company, snapshot, get):
    # Public widget endpoint: published jobs only, without applicant/API credentials.
    payload = get('https://apply.workable.com/api/v1/widget/accounts/'
                  + quote(company['slug'], safe='') + '?details=true')
    if not isinstance(payload, dict) or not isinstance(payload.get('name'), str) or not payload['name'].strip():
        raise ValueError('Missing Workable employer identity')
    by_id = {}
    for row in rows(payload, 'jobs'):
        identifier = row.get('shortcode')
        if not isinstance(identifier, str) or not identifier:
            raise ValueError('Missing Workable posting identity')
        locations = rows(row.get('locations', []))
        parts = [row.get('city'), row.get('state'), row.get('country')]
        if singapore('', row.get('country')):
            parts.append('Singapore')
        for location in locations:
            if location.get('hidden') is not True:
                parts.extend([location.get('city'), location.get('region'), location.get('country')])
                if location.get('countryCode') == 'SG':
                    parts.append('Singapore')
        if any(part is not None and not isinstance(part, str) for part in parts):
            raise ValueError('Invalid Workable location')
        location = '; '.join(dict.fromkeys(part.strip() for part in parts if part and part.strip()))
        url = row.get('url') or ''
        if urlsplit(url).scheme != 'https' or not urlsplit(url).netloc:
            raise ValueError('Missing Workable application URL')
        # Missing detail text would lose intake evidence; protect existing history.
        if not isinstance(row.get('description'), str) or not row['description'].strip():
            raise ValueError('Missing Workable description')
        employment_type = row.get('employment_type')
        if isinstance(employment_type, str) and employment_type.lower() in {'intern', 'internship'}:
            employment_type = 'Intern'
        job = record(company, identifier, row.get('title'), location, url,
            row['description'], row.get('country'), row.get('published_on'),
            employment_type=employment_type)
        # The widget emits one representation per location, with one shortcode.
        # Merge only location differences; conflicting job content is incomplete.
        if identifier in by_id:
            previous = by_id[identifier]
            if any(previous[key] != value for key, value in job.items()
                   if key not in {'country', 'location'}):
                raise ValueError('Conflicting Workable posting identity')
            previous['location'] = '; '.join(dict.fromkeys(
                previous['location'].split('; ') + location.split('; ')))
        else:
            by_id[identifier] = job
            snapshot.jobs.append(job)
    snapshot.complete = True
