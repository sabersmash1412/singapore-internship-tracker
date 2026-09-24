"""Display-only period hints; never use inferred dates to close a listing."""
import calendar
import re
from datetime import date

from .classify import MONTH

MONTHS = {name.lower(): index for index, name in enumerate(calendar.month_abbr) if name}


def period_end(value):
    """Return a conservative display boundary for a recognized advertised period."""
    value = value.strip()
    match = re.fullmatch(rf'({MONTH})\s*(20\d{{2}})?\s*(?:-|–|—|to|till|through)\s*({MONTH})\s+(20\d{{2}})', value, re.I)
    if match:
        start, start_year, end, year = match.groups()
        month, year = MONTHS[end[:3].lower()], int(year)
        if start_year and (int(start_year), MONTHS[start[:3].lower()]) > (year, month):
            return None
    else:
        match = re.fullmatch(r'(H[12]|Spring|Summer|Fall|Winter)\s+(20\d{2})', value, re.I)
        if match:
            label, year = match.group(1).lower(), int(match.group(2))
            month = {'h1': 6, 'h2': 12, 'spring': 5, 'summer': 8, 'fall': 11, 'winter': 3}[label]
            # Winter can cross a year boundary; keep it visible through next March.
            if label == 'winter':
                year += 1
        else:
            # A start month is not an end date. Keep it through its stated year.
            match = re.fullmatch(rf'(?:{MONTH}\s+)?(20\d{{2}})\s+(Start|Intake)', value, re.I)
            if not match:
                return None
            year, month = int(match.group(1)), 12
    return date(year, month, calendar.monthrange(year, month)[1])


def older_period(value, as_of):
    if not value or not as_of:
        return False
    ends = [period_end(part) for part in value.split(' / ')]
    return all(end is not None and end < as_of for end in ends)
