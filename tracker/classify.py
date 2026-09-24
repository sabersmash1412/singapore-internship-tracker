"""Conservative classification. Missing information stays missing."""
import html
import re
from html.parser import HTMLParser


class TextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def plain(value):
    parser = TextParser()
    parser.feed(html.unescape(value or ""))
    return re.sub(r"\s+", " ", " ".join(parser.parts)).strip()


def singapore(location, country=None):
    # Country codes are trusted only in a structured country field.
    return str(country or "").lower() in {"sg", "sgp", "singapore"} or bool(
        re.search(r"\bsingapore\b", location, re.I)
    )


def category(title):
    # A recruiting role for an AI team is still recruiting, not an AI internship.
    if re.search(r'\b(talent acquisition|recruiter|recruitment|human resources|hr operations)\b', title, re.I):
        return None
    patterns = [
        ("Data & AI", r"\b(data|analytics|machine learning|ai|ml|algorithm|algorithms|research scientist|computer vision)\b"),
        ("Security", r"\b(cyber\w*|security)\b"),
        ("Quant", r"\b(quant\w*|trading|trader)\b"),
        ("Software", r"\b(software|developer|backend|frontend|full.?stack|automation|devops|sre|qa)\b"),
        ("Hardware", r"\b(hardware|firmware|embedded|semiconductor|electrical)\b"),
        ("IT & Infrastructure", r"\b(it|information technology|cloud|network|systems?|data\s?cent(?:er|re)|site reliability|(?:it|technology|cloud|network) infrastructure|infrastructure engineer(?:ing)?)\b"),
    ]
    for label, pattern in patterns:
        if re.search(pattern, title, re.I):
            return label
    return None


def eligible(job):
    return (
        singapore(job["location"], job.get("country"))
        and (bool(re.search(r"\b(intern|internship|internships|co[ -]?op)\b", job["title"], re.I))
             or job.get("employment_type") in {"Intern", "Internship"})
        and (category(job["title"]) or job.get("role_category")) is not None
    )


MONTH = r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
PERIOD = re.compile(
    rf"\b(?:{MONTH}\s*(?:20\d{{2}})?\s*(?:-|–|—|to|through)\s*{MONTH}\s+20\d{{2}}|"
    r"(?:H[12]|Summer|Winter|Fall|Spring)\s+20\d{2}|20\d{2}\s+(?:Start|Intake))\b", re.I
)


def enrich(job):
    description = plain(job.pop("description", ""))
    job["category"] = job.get("role_category") or category(job["title"])
    # Title is strongest. Description matches require internship context to avoid
    # mistaking a company history or graduation date for the internship period.
    matches = list(PERIOD.finditer(job["title"]))
    evidence = job["title"] if matches else None
    if not matches:
        for sentence in re.split(r"(?<=[.!?])\s+", description):
            if re.search(r"\b(internship|intern|availability|start date|intake)\b", sentence, re.I):
                matches = list(PERIOD.finditer(sentence))
                if matches:
                    evidence = sentence
                    break
    periods = list(dict.fromkeys(match.group(0) for match in matches))
    job["period"] = ' / '.join(periods) or None
    job["period_evidence"] = evidence
    duration = re.search(
        r"\b(?:minimum(?: of)?|at least|duration(?: of)?|commit(?:ment)?(?: of| to)?)\s+"
        r"(\d{1,2}(?:\s*[-–]\s*\d{1,2})?\s*(?:months?|weeks?))\b", description, re.I
    )
    structured_duration = job.pop("structured_duration", None)
    job["duration"] = structured_duration or (duration.group(1) if duration else None)
    job["duration_evidence"] = structured_duration or (duration.group(0) if duration else None)
    # An employer questionnaire or a lack of restrictions is not eligibility evidence.
    job["eligibility"] = "Not extracted — check employer posting"
    return job
