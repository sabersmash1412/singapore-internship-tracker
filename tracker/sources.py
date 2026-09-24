"""Public read-only feeds. Completeness is required before considering closures."""
import json
import time
from dataclasses import dataclass, field
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen

from .classify import eligible, plain


@dataclass
class Snapshot:
    board: str
    jobs: list = field(default_factory=list)
    complete: bool = False
    error: str | None = None
    warnings: list = field(default_factory=list)


def request(url, body=None, headers=None, as_text=False):
    for attempt in range(3):
        try:
            req = Request(url, data=json.dumps(body).encode() if body is not None else None,
                          headers={"User-Agent": "singapore-internship-tracker/0.2", "Accept": "application/json",
                                   "Content-Type": "application/json", **(headers or {})})
            with urlopen(req, timeout=25) as response:
                return response.read().decode('utf-8') if as_text else json.load(response)
        except (HTTPError, URLError, TimeoutError) as exc:
            if isinstance(exc, HTTPError) and exc.code not in {429, 500, 502, 503, 504}:
                raise
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def get_json(url):
    return request(url)


def post_json(url, body, headers=None):
    return request(url, body=body, headers=headers)


def get_text(url):
    return request(url, as_text=True)


def rows(payload, key=None):
    if key:
        if not isinstance(payload, dict) or payload.get("error") or payload.get("errors"):
            raise ValueError("Invalid feed envelope")
        payload = payload.get(key)
    if not isinstance(payload, list) or any(not isinstance(row, dict) for row in payload):
        raise ValueError("Feed did not contain a list of job objects")
    return payload


def normalized(company, row):
    platform, slug = company["platform"], company["slug"]
    if platform == "greenhouse":
        title, location = row.get("title"), (row.get("location") or {}).get("name")
        url, description = row.get("absolute_url"), row.get("content", "")
        # updated_at is not a posting date.
        posted, country = row.get("first_published"), None
    elif platform == "lever":
        categories = row.get("categories") or {}
        title = row.get("text")
        location = "; ".join(categories.get("allLocations") or [categories.get("location", "")])
        url = row.get("hostedUrl")
        description = " ".join([row.get("descriptionPlain", ""), row.get("additionalPlain", "")] + [plain(x.get("content", "")) for x in row.get("lists", [])])
        # createdAt describes record creation, not necessarily public release.
        posted, country = None, row.get("country")
    else:
        loc = row.get("location") or {}
        title = row.get("name")
        location = loc.get("fullLocation") or ", ".join(filter(None, [loc.get("city"), loc.get("country")]))
        country = loc.get("country")
        url = f"https://jobs.smartrecruiters.com/{quote(slug, safe='')}/{quote(str(row.get('id', '')), safe='')}"
        posted, description = row.get("releasedDate"), ""
    identifier = row.get("id")
    if not identifier or not isinstance(title, str) or not title.strip() or not isinstance(location, str) or not location.strip():
        raise ValueError("Job missing identity, title or location")
    if not isinstance(url, str) or urlsplit(url).scheme != "https" or not urlsplit(url).netloc:
        raise ValueError("Job missing a valid HTTPS application URL")
    board = f"{platform}:{slug}"
    return dict(id=f"{board}:{identifier}", board=board, company=company["name"],
                title=title.strip(), location=location, country=country, url=url,
                posted_at=posted, description=description, source=platform)


def fetch(company, get=get_json, post=post_json, text=get_text):
    platform, slug = company["platform"], quote(company["slug"], safe="")
    snapshot = Snapshot(f"{platform}:{company['slug']}")
    try:
        if platform in {"bytedance", "workday", "sea", "shopee", "govtech"}:
            from .regional import collect
            collect(company, snapshot, get, post, text)
            return snapshot
        raw = []
        if platform == "greenhouse":
            raw = rows(get(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"), "jobs")
        else:
            seen = set()
            for offset in range(0, 10000, 100):
                if platform == "lever":
                    payload = get(f"https://api.lever.co/v0/postings/{slug}?mode=json&limit=100&skip={offset}")
                    page = rows(payload)
                    total = None
                elif platform == "smartrecruiters":
                    payload = get(f"https://api.smartrecruiters.com/v1/companies/{slug}/postings?limit=100&offset={offset}")
                    page = rows(payload, "content")
                    total = payload.get("totalFound")
                    if type(total) is not int or total < 0:
                        raise ValueError("Missing or invalid pagination total")
                else:
                    raise ValueError(f"Unsupported platform: {platform}")
                ids = [str(row.get("id", "")) for row in page]
                if any(not identifier or identifier in seen for identifier in ids) or len(ids) != len(set(ids)):
                    raise ValueError("Repeated or invalid pagination IDs")
                seen.update(ids)
                raw.extend(page)
                if total is not None and len(raw) >= total:
                    break
                if len(page) < 100:
                    if total is not None and len(raw) < total:
                        raise ValueError("Feed ended before reported total")
                    break
            else:
                raise ValueError("Pagination cap reached")
        for row in raw:
            snapshot.jobs.append(normalized(company, row))
        if len({job["id"] for job in snapshot.jobs}) != len(snapshot.jobs):
            raise ValueError("Duplicate job IDs in snapshot")
        snapshot.complete = True
        if platform == "smartrecruiters":
            for job in snapshot.jobs:
                if eligible(job):
                    try:
                        detail = get(f"https://api.smartrecruiters.com/v1/companies/{slug}/postings/{quote(job['id'].rsplit(':', 1)[1], safe='')}")
                        sections = detail["jobAd"]["sections"]
                        job["description"] = " ".join(value.get("text", "") for value in sections.values() if isinstance(value, dict))
                    except Exception as exc:
                        job["detail_unavailable"] = True
                        snapshot.warnings.append(f"Detail unavailable for {job['id']}: {type(exc).__name__}")
    except Exception as exc:
        snapshot.complete = False
        snapshot.error = f"{type(exc).__name__}: {exc}"
    return snapshot
