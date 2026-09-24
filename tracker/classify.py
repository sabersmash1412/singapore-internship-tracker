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
    if re.search(r'\b(talent acquisition|recruiter|recruitment|human resources|hr operations|hr business partner|hrbp|business development and commercial)\b', title, re.I):
        return None
    # Team names alone do not make administrative project coordination technical.
    if re.search(r"\bproject management\b", title, re.I):
        title = re.sub(r"[（(].*?[）)]", "", title)
    title = re.sub(r"\b(?:AWS\s+)?Cloud Logistics\b", "", title, flags=re.I)
    if re.search(r"\b(?:physical security|DC Security Specialist)\b", title, re.I):
        return None
    if re.search(r"\bbusiness intelligence\s*(?:\(BI\)\s*)?intern(?:ship)?\b", title, re.I):
        return "Data & AI"
    if re.search(r"\bproduct builder intern(?:ship)?\s*\(product engineering\)", title, re.I):
        return "Software"
    patterns = [
        ("Data & AI", r"\b(data|analytics|machine learning|large language model|llm|prompt engineering|ai|ml|algorithm|algorithms|research scientist|computer vision)\b"),
        ("Security", r"\b(cyber\w*|security)\b"),
        ("Quant", r"\b(quant\w*|trading|trader)\b"),
        ("Software", r"\b(software|developer|backend|frontend|full.?stack|automation|devops|sre|qa)\b"),
        ("Hardware", r"\b(hardware|firmware|embedded|semiconductor|electrical|hybrid bonding|process integration|pvd|cvd|3dic|cmos|testchip|esd device|silicon photonics|silicon design|nand validation|test solutions engineer(?:ing)?|optical characterization|diagnostic design|ic design|server test)\b"),
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
    rf"(?:H[12]|[12]H|Summer|Winter|Fall|Spring)\s+20\d{{2}}|20\d{{2}}\s+(?:Start|Intake)|{MONTH}\s+20\d{{2}}(?:\s+(?:Start|Intake))?)\b", re.I
)


# Dates about eligibility or applications are not internship intake evidence.
NON_INTAKE = re.compile(r"\b(graduat\w*|application\s+(?:deadline|window|period)|applications?\s+(?:close|open|due)|apply\s+(?:by|before)|deadline|closing date|interview\w*|assessment\w*|founded|established)\b", re.I)
INTAKE_CONTEXT = re.compile(r"\b(internships?|intern|availability|start date|intake|starting|starts?|commenc\w*|available\s+from)\b", re.I)


def extract_period(title, description):
    candidates = [title] + re.split(r"(?<=[.!?;])\s+|\s+-\s+(?=(?:Able to|Available|Internship|Start date)\b)", description, flags=re.I)
    for index, evidence in enumerate(candidates):
        if NON_INTAKE.search(evidence):
            continue
        if index and not INTAKE_CONTEXT.search(evidence):
            continue
        # Day numbers should not split a range into two apparent starts.
        matching = re.sub(rf'\b\d{{1,2}}(?:st|nd|rd|th)?\s+(?={MONTH}\b)', '', evidence, flags=re.I)
        # Explicit end-date clauses may contain multiple alternative end dates.
        matching = re.split(r'\bend date\s*:', matching, maxsplit=1, flags=re.I)[0]
        periods = []
        matches = list(PERIOD.finditer(matching))
        single = re.compile(rf'{MONTH}\s+20\d{{2}}', re.I)
        strong = [m for m in matches if not single.fullmatch(m.group(0))]
        # Prefer a stated range/half-year to stray month fragments inside it.
        # E.g. H1 2027 (Dec 2026/Jan 2027 to May/June 2027).
        ambiguous = re.search(rf'{MONTH}\s*(?:20\d{{2}})?\s*/\s*{MONTH}', matching, re.I)
        if ambiguous:
            if not strong:
                continue
            matches = strong
        for match in matches:
            if single.fullmatch(match.group(0)) and re.search(
                    r'\b(?:until|through|to|ending|ends|end date|concludes)(?:\s+(?:in|on|at))?\s*:?\s*$',
                    matching[:match.start()], re.I):
                continue
            value = match.group(0)
            # Normalize aliases, retaining the original sentence as evidence.
            value = re.sub(r'^([12])H\b', r'H\1', value, flags=re.I)
            if re.fullmatch(rf'{MONTH}\s+20\d{{2}}', value, re.I):
                value += ' Start'
            if value not in periods:
                periods.append(value)
        if periods:
            return ' / '.join(periods), evidence
    return None, None


def enrich(job):
    description = plain(job.pop("description", ""))
    job["category"] = job.get("role_category") or category(job["title"])
    # Prefer title evidence; otherwise accept a sentence with intake context.
    job["period"], job["period_evidence"] = extract_period(job["title"], description)
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
