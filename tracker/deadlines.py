"""Only explicit employer deadlines may close an application window."""
import re
from datetime import datetime
from zoneinfo import ZoneInfo

from .classify import plain


def govtech_deadline(html):
    text = plain(html)
    matches = re.findall(
        r'internship applications are (?:now )?open until\s+(\d{1,2}\s+[A-Za-z]+\s+20\d{2}),?\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b',
        text, re.I)
    if not matches or len(set(matches)) != 1:
        raise ValueError('GovTech application deadline missing or ambiguous')
    day, hour, minute, meridiem = matches[0]
    parsed = datetime.strptime(f'{day} {hour}:{minute or "00"}{meridiem}', '%d %B %Y %I:%M%p')
    return parsed.replace(tzinfo=ZoneInfo('Asia/Singapore')).isoformat()


def deadline_passed(job, now):
    value = job.get('application_deadline_at')
    if not value:
        return False
    deadline = datetime.fromisoformat(value.replace('Z', '+00:00'))
    checked = datetime.fromisoformat(now.replace('Z', '+00:00'))
    if deadline.tzinfo is None or checked.tzinfo is None:
        raise ValueError('Application deadlines require an explicit timezone')
    return checked >= deadline
