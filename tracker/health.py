"""Check saved source health without changing collected jobs or artifacts."""


def check(current, companies):
    expected = [f"{c['platform']}:{c['slug']}" for c in companies]
    reports = current.get('sources')
    if not expected or len(expected) != len(set(expected)):
        raise ValueError('Missing or duplicate registered sources')
    if not isinstance(reports, list) or any(not isinstance(r, dict) for r in reports):
        raise ValueError('Missing or malformed source health reports')
    actual = [r.get('board') for r in reports]
    if len(actual) != len(expected) or set(actual) != set(expected):
        raise ValueError('Source health reports do not match the employer registry')
    failed = [r['board'] for r in reports
              if r.get('complete') is not True or r.get('error') or r.get('warnings')]
    if failed:
        raise ValueError('Incomplete employer feeds: ' + ', '.join(failed) +
                         '. Inspect README source health; this check does not change saved listings.')
    return len(expected)
