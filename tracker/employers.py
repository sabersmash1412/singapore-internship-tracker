"""Public employer searches with checked pagination and explicit locations."""
import json
from datetime import datetime
from urllib.parse import urlencode, quote

from .classify import eligible
from .regional import checked_page, record
from .sources import rows


def apple_data(html, section):
    marker = 'window.__staticRouterHydrationData = JSON.parse('
    if html.count(marker) != 1:
        raise ValueError('Missing or ambiguous Apple search data')
    encoded, _ = json.JSONDecoder().raw_decode(html.split(marker, 1)[1])
    return json.loads(encoded)['loaderData'][section]


def locations(values):
    result = []
    for value in rows(values):
        parts = [value.get('name'), value.get('city'), value.get('countryName')]
        label = ', '.join(dict.fromkeys(x for x in parts if x))
        if not label:
            raise ValueError('Missing posting location')
        result.append(label)
    return '; '.join(result)


def collect(company, snapshot, get, text):
    platform = company['platform']
    seen, expected = set(), None
    for page_number in range(1, 101):
        if platform == 'amazon':
            # Read the full keyword search; loc_query alone is not a country filter.
            data = get(company['api_base'] + '?' + urlencode(dict(base_query='intern', offset=len(seen), result_limit=100)))
            page, total, key = rows(data, 'jobs'), data.get('hits'), 'id_icims'
        elif platform == 'amd':
            data = get(company['api_base'] + '?' + urlencode(dict(keywords='intern', location='Singapore', page=page_number)))
            page = [row['data'] for row in rows(data, 'jobs')]
            rows(page)
            total, key = data.get('totalCount'), 'slug'
        elif platform == 'apple':
            data = apple_data(text(company['careers_url'] + '&page=' + str(page_number)), 'search')
            page, total, key = rows(data, 'searchResults'), data.get('totalRecords'), 'id'
        else:
            raise ValueError('Unsupported employer')
        if expected is None:
            expected = total
        elif total != expected:
            raise ValueError('Search total changed during pagination')
        done = checked_page(page, total, seen, key)
        for row in page:
            if platform == 'amazon':
                extra_locations = [json.loads(value) for value in row.get('locations', [])]
                location = '; '.join(filter(None, [row.get('location'), *[
                    ', '.join(filter(None, [v.get('city'), v.get('normalizedCountryName')])) for v in extra_locations]]))
                path = row.get('job_path') or ''
                if not path.startswith('/en/jobs/'):
                    raise ValueError('Invalid Amazon posting URL')
                posted = datetime.strptime(row['posted_date'], '%B %d, %Y').date().isoformat() if row.get('posted_date') else None
                job = record(company, row[key], row.get('title'), location, 'https://www.amazon.jobs' + path,
                    '\n'.join(row.get(k) or '' for k in ['description', 'basic_qualifications', 'preferred_qualifications']),
                    row.get('country_code'), posted)
            elif platform == 'amd':
                job = record(company, row[key], row.get('title'), row.get('full_location'),
                    company['careers_url'] + '/' + quote(str(row[key]), safe=''), row.get('description') or '',
                    row.get('country'), row.get('posted_date'))
            else:
                title, location = row.get('postingTitle'), locations(row.get('locations'))
                if not eligible(dict(title=title, location=location)):
                    continue
                url = 'https://jobs.apple.com/en-us/details/' + quote(str(row[key]), safe='') + '/' + quote(row['transformedPostingTitle'], safe='')
                detail = apple_data(text(url), 'jobDetails')['jobsData']
                if detail.get('jobNumber') != row[key] or not detail.get('description'):
                    raise ValueError('Incomplete or mismatched Apple detail')
                job = record(company, row[key], detail.get('postingTitle'), locations(detail.get('locations')), url,
                    '\n'.join(detail.get(k) or '' for k in ['jobSummary', 'description', 'minimumQualifications', 'preferredQualifications']),
                    posted=detail.get('postingDateMeta'))
            snapshot.jobs.append(job)
        if done:
            snapshot.complete = True
            return
    raise ValueError('Employer pagination cap reached')
