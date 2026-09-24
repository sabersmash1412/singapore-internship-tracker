"""Publish the student-facing README and downloadable data exports."""
import csv
import html
import re
from datetime import datetime, timedelta
from urllib.parse import quote
from zoneinfo import ZoneInfo

from .state import write_json

START = '<!-- INTERNSHIPS:START -->'
END = '<!-- INTERNSHIPS:END -->'


def cell(value):
    text = html.escape(str(value or 'Not stated'), quote=False)
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'([\\`*_\[\]])', r'\\\1', text)
    return text.replace('|', '&#124;')


def instant(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def day(value):
    return instant(value).astimezone(ZoneInfo('Asia/Singapore')).strftime('%d %b %Y') if value else 'Not stated'


def publish(root, state):
    readme_path = root / 'README.md'
    readme = readme_path.read_text()
    if readme.count(START) != 1 or readme.count(END) != 1 or readme.index(START) >= readme.index(END):
        raise ValueError('README must contain exactly one ordered internship marker pair')
    jobs = sorted((j for j in state['jobs'].values() if j['is_open']),
                  key=lambda j: (j['first_seen_at'], j['company'], j['title'], j['id']), reverse=True)
    as_of = instant(state['last_attempt_at']) if state['last_attempt_at'] else None
    stamp = as_of.astimezone(ZoneInfo('Asia/Singapore')).strftime('%d %b %Y, %H:%M SGT') if as_of else 'Not collected yet'
    lines = [f'**{len(jobs)} open internships · {len({j["company"] for j in jobs})} employers with roles**', '',
             f'Last collection: **{stamp}**. Scheduled every 30 minutes; runs may be delayed.', '',
             '🆕 = first seen within 48 hours of the collection above. First seen is when this tracker discovered a role, not when the employer posted it. Initial collection marks all newly discovered roles as new.', '',
             '## Open internships', '',
             '| Company | Role | Apply | Period | Employer posted | First seen |',
             '| --- | --- | --- | --- | --- | --- |']
    for job in jobs:
        new = as_of and timedelta(0) <= as_of - instant(job['first_seen_at']) <= timedelta(hours=48)
        url = quote(job['url'], safe=':/?=&%#@+;,~!-._')
        lines.append('| ' + ' | '.join([cell(job['company']), ('🆕 ' if new else '') + cell(job['title']),
                     f'[Apply](<{url}>)', cell(job.get('period')), day(job.get('posted_at')), day(job['first_seen_at'])]) + ' |')
    if not jobs:
        lines += ['', 'No matching open internships in the latest saved data.']
    closed = sorted((j for j in state['jobs'].values() if not j['is_open'] and as_of and j.get('closed_at') and
                     timedelta(0) <= as_of - instant(j['closed_at']) <= timedelta(days=14)),
                    key=lambda j: (j['closed_at'], j['id']), reverse=True)
    if closed:
        lines += ['', '<details>', '<summary>Recently closed / removed from scope (last 14 days)</summary>', '',
                  '| Company | Role | Closed |', '| --- | --- | --- |']
        lines += [f'| {cell(j["company"])} | {cell(j["title"])} | {day(j["closed_at"])} |' for j in closed]
        lines += ['', '</details>']
    lines += ['', '<details>', '<summary>Source coverage and collection health</summary>', '',
              '| Source board | Latest check | Matching roles returned |', '| --- | --- | --- |']
    for source in state['sources']:
        status = 'Complete' if source['complete'] else '⚠️ Incomplete — previous listings retained'
        if source.get('warnings'):
            status += f'; {len(source["warnings"])} details unavailable'
        lines.append(f'| {cell(source["board"])} | {status} | {source["matched"]} |')
    lines += ['', 'A failed source can leave older listings visible. Check the collection date above and confirm availability on the employer’s page.', '', '</details>']
    generated = '\n'.join(lines)
    updated = readme.split(START)[0] + START + '\n\n' + generated + '\n\n' + END + readme.split(END)[1]
    data = root / 'data'
    write_json(data / 'jobs.json', {'updated_at': state['last_attempt_at'], 'jobs': jobs, 'sources': state['sources']})
    fields = ['company', 'title', 'category', 'location', 'period', 'duration', 'posted_at', 'first_seen_at', 'last_seen_at', 'url']
    with (data / 'internships.csv').open('w', newline='') as output:
        writer = csv.DictWriter(output, fields)
        writer.writeheader()
        for job in jobs:
            values = {key: job.get(key) or '' for key in fields}
            writer.writerow({key: "'" + value if value.lstrip().startswith(('=', '+', '-', '@')) else value for key, value in values.items()})
    temporary = readme_path.with_suffix('.md.tmp')
    temporary.write_text(updated)
    temporary.replace(readme_path)
