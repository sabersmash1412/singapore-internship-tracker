"""Employer-specific public feeds verified against their official career sites."""
import json
import re
from urllib.parse import quote, urlencode

from .classify import category, singapore
from .sources import rows


def record(company, identifier, title, location, url, description='', country=None, posted=None, **extra):
    if not identifier or not isinstance(title, str) or not title.strip() or not location or not url.startswith('https://'):
        raise ValueError('Job missing identity, title, location or HTTPS URL')
    board = f"{company['platform']}:{company['slug']}"
    return dict(id=f'{board}:{identifier}', board=board, company=company['name'], title=title.strip(),
                location=location, country=country, url=url, posted_at=posted,
                description=description, source=company['platform'], **extra)


def checked_page(page, total, seen, key):
    rows(page)
    if type(total) is not int or total < 0:
        raise ValueError('Missing or invalid pagination total')
    ids = [str(row.get(key) or '') for row in page]
    if any(not x or x in seen for x in ids) or len(ids) != len(set(ids)):
        raise ValueError('Repeated or missing pagination identity')
    seen.update(ids)
    if len(seen) > total or (not page and len(seen) < total):
        raise ValueError('Pagination count mismatch')
    return len(seen) == total


def supplier(company, snapshot, post):
    base = company['api_base']
    headers = {'website-path': company['website_path'], 'accept-language': 'en-US', 'origin': company['careers_url'].split('/search')[0]}
    # Resolve the location and internship type from the current official filters.
    filters = post(base + '/config/job/filters', {}, headers)
    if filters.get('code') != 0 or not isinstance(filters.get('data'), dict):
        raise ValueError('Invalid career filter response')
    data = filters['data']
    cities = [x['code'] for x in rows(data, 'city_list') if x.get('en_name') == 'Singapore']
    # recruit_type IDs are stable site enum values; confirmed in actual postings.
    if not cities:
        raise ValueError('Singapore is absent from location filters')
    seen = set()
    for _ in range(100):
        offset = len(seen)
        response = post(base + '/search/job/posts', {
            'keyword': '', 'recruitment_id_list': ['202'], 'location_code_list': cities,
            'limit': 100, 'offset': offset,
        }, headers)
        if response.get('code') != 0 or not isinstance(response.get('data'), dict):
            raise ValueError('Career search returned an error')
        data = response['data']
        page = rows(data, 'job_post_list')
        done = checked_page(page, data.get('count'), seen, 'id')
        for row in page:
            city = row.get('city_info') or {}
            location = city.get('en_name') or city.get('name')
            if not location:
                raise ValueError('Missing job location')
            employment = (row.get('recruit_type') or {}).get('en_name')
            snapshot.jobs.append(record(company, row['id'], row.get('title'), location,
                company['careers_url'].rstrip('/') + '/' + quote(str(row['id']), safe=''),
                '\n'.join([row.get('description') or '', row.get('requirement') or '']),
                employment_type=employment))
        if done:
            snapshot.complete = True
            return
    raise ValueError('Career search pagination cap reached')


def workday(company, snapshot, get, post):
    base = company['api_base']
    seen = set()
    expected_total = None
    for offset in range(0, 4000, 20):
        data = post(base + '/jobs', {'appliedFacets': {}, 'limit': 20, 'offset': offset, 'searchText': 'intern'})
        page = rows(data, 'jobPostings')
        total = data.get('total')
        if expected_total is None:
            expected_total = total
        elif total not in (0, expected_total):
            raise ValueError('Workday total changed during pagination')
        # Workday reports zero on subsequent pages on these tenants, even
        # while returning records. The first-page total defines completeness.
        done = checked_page(page, expected_total, seen, 'externalPath')
        for row in page:
            path, title = row['externalPath'], row.get('title')
            if not isinstance(title, str) or not title.strip() or not path.startswith('/job/'):
                raise ValueError('Malformed Workday job')
            # Search may match descriptions, including "internal". Only detail
            # requests for internship titles are needed for this tracker scope.
            if not re.search(r'\b(intern|internships?|co[ -]?op)\b', title, re.I):
                continue
            location = row.get('locationsText') or 'Location not stated'
            description, country, posted = '', None, None
            try:
                detail = get(base + path)['jobPostingInfo']
                if not isinstance(detail, dict) or not detail.get('title'):
                    raise ValueError('Missing Workday posting detail')
                description = detail.get('jobDescription') or ''
                location = '; '.join(filter(None, [detail.get('location'), *(detail.get('additionalLocations') or [])])) or location
                country = (detail.get('country') or {}).get('descriptor')
                posted = detail.get('startDate')
            except Exception as exc:
                # Unknown location could conceal a Singapore role. Preserve old
                # state on this board rather than closing on partial evidence.
                snapshot.warnings.append(f'Detail unavailable: {path}: {type(exc).__name__}')
            identifier = path.rsplit('/', 1)[-1]
            job = record(company, identifier, title, location,
                         company['careers_url'].rstrip('/') + path, description, country, posted)
            if not description:
                job['detail_unavailable'] = True
            snapshot.jobs.append(job)
        if done:
            snapshot.complete = not snapshot.warnings
            if snapshot.warnings:
                snapshot.error = 'Incomplete Workday detail coverage'
            return
    raise ValueError('Workday pagination cap reached')


def flight_text(html):
    """Decode the site's public server-rendered data, without executing JS."""
    chunks = []
    for match in re.finditer(r'self\.__next_f\.push\((\[.*?\])\)</script>', html, re.S):
        value = json.loads(match.group(1))
        if len(value) > 1 and value[0] == 1 and isinstance(value[1], str):
            chunks.append(value[1])
    if not chunks:
        raise ValueError('Missing server-rendered catalogue')
    return ''.join(chunks)


def govtech(company, snapshot, text):
    html = text(company['careers_url'])
    flight = flight_text(html)
    matches = list(re.finditer(r'"internships":', flight))
    if len(matches) != 1:
        raise ValueError('Missing or ambiguous internship catalogue')
    catalogue, _ = json.JSONDecoder().raw_decode(flight[matches[0].end():].lstrip())
    if not isinstance(catalogue, dict) or not catalogue:
        raise ValueError('Empty or malformed internship catalogue')
    tech_roles = {'cybersecurity-engineer', 'data-engineer', 'data-scientist', 'software-engineer', 'systems-engineer'}
    if not tech_roles.issubset(catalogue):
        raise ValueError('Incomplete technical role groups')
    seen = set()
    for role, projects in catalogue.items():
        for project in rows(projects):
            if not project.get('id') or type(project.get('filled')) is not bool:
                raise ValueError('Project missing identity or availability')
            if project['id'] in seen:
                raise ValueError('Duplicate project ID')
            seen.add(project['id'])
            if role not in tech_roles or project['filled']:
                continue
            title = project.get('projectTitle')
            location = project.get('workLocation') or 'Location not stated'
            # Explicit SG postal notation and this named SG district are source
            # address evidence. "Others" remains unknown and is filtered out.
            country = 'SG' if re.search(r'\(S\d{6}\)', location) or location == 'Punggol Digital District' else None
            slug = project.get('projectSlug')
            if not slug or project.get('roleSlug') != role:
                raise ValueError('Project route missing or inconsistent')
            description = project.get('projectDescription') or ''
            if description.startswith('$'):
                description = ''  # unresolved RSC reference; never invent text
            durations = project.get('internshipDurations')
            if not isinstance(durations, list) or not all(isinstance(x, str) for x in durations):
                raise ValueError('Invalid structured internship duration')
            snapshot.jobs.append(record(company, project['id'], title, location,
                company['careers_url'].rstrip('/') + '/' + quote(role, safe='') + '/' + quote(slug, safe=''),
                description, country, employment_type='Intern',
                structured_duration=' / '.join(durations) or None,
                role_category=category(project.get('role') or '')))
    snapshot.complete = True


def collect(company, snapshot, get, post, text):
    platform = company['platform']
    if platform == 'bytedance':
        supplier(company, snapshot, post)
    elif platform == 'workday':
        workday(company, snapshot, get, post)
    elif platform == 'govtech':
        govtech(company, snapshot, text)
    elif platform in {'sea', 'shopee'}:
        sea(company, snapshot, get)
    else:
        raise ValueError('Unsupported regional platform')


def sea(company, snapshot, get):
    # Shared official ATS metadata maps numeric IDs to names. Never infer
    # Singapore from a company's HQ or from a remembered numeric location ID.
    metadata = get('https://ats.workatsea.com/ats/api/v1/user/meta/slice/?flags=2064&from_career=true')
    if metadata.get('code') != 0 or not isinstance(metadata.get('data'), dict):
        raise ValueError('Invalid Sea location metadata')
    locations = {row['city_id']: row for row in rows(metadata['data'], 'flat_locations')}
    levels = {row['employment_level_id']: row['employment_type_name'] for row in rows(metadata['data'], 'employment_level_list')}
    city_ids = [key for key, row in locations.items() if row.get('region_abbr') == 'SG']
    intern_ids = [key for key, label in levels.items() if label == 'Internship']
    if not city_ids or not intern_ids:
        raise ValueError('Missing Singapore or internship metadata')
    seen = set()
    for _ in range(100):
        offset = len(seen)
        params = [('limit', 100), ('offset', offset)]
        params += [('city_ids', x) for x in city_ids] + [('employment_ids', x) for x in intern_ids]
        if company['platform'] == 'sea':
            params += [('external_entity_id', 3), ('post_type', 1)]
        data = get(company['api_base'] + '/user/job/list/?' + urlencode(params))
        if data.get('code') != 0 or not isinstance(data.get('data'), dict):
            raise ValueError('Sea job search returned an error')
        data = data['data']
        page = rows(data, 'job_list')
        done = checked_page(page, data.get('total_count'), seen, 'job_id')
        for row in page:
            loc = locations.get(row.get('city_id'))
            if not loc:
                raise ValueError('Unmapped job city')
            # Shopee's site also carries Monee (post_type 4); don't mislabel it.
            if company['platform'] == 'shopee' and row.get('external_entity_id') != 1:
                continue
            country = loc.get('region_abbr')
            identifier = row['job_id']
            if company['platform'] == 'sea':
                url = 'https://career.sea.com/position/' + quote(identifier, safe='')
            else:
                url = 'https://careers.shopee.sg/job-detail/' + quote(identifier, safe='') + '/1'
            snapshot.jobs.append(record(company, identifier, row.get('job_name'),
                loc['city_name'] + ', ' + loc['region_name'], url,
                (row.get('job_description') or '') + '\n' + (row.get('requirements') or ''), country,
                employment_type=levels.get(row.get('employment_id'))))
        if done:
            snapshot.complete = True
            return
    raise ValueError('Sea pagination cap reached')
