"""Static artifacts: no runtime server or account required."""
import csv
import json
import shutil
import xml.etree.ElementTree as ET

from .state import write_json


def publish(root, state):
    docs = root / "docs"
    docs.mkdir(exist_ok=True)
    jobs = sorted((job for job in state["jobs"].values() if job["is_open"]),
                  key=lambda j: (j["first_seen_at"], j["company"], j["title"], j["id"]), reverse=True)
    payload = {"updated_at": state["last_attempt_at"], "jobs": jobs, "sources": state["sources"]}
    write_json(docs / "api/jobs.json", payload)
    # Embed data for file:// previews and avoid a separate stale JSON fetch.
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    template = (root / "web/index.html").read_text()
    (docs / "index.html").write_text(template.replace("__TRACKER_DATA__", encoded))
    for name in ("app.js", "style.css"):
        shutil.copyfile(root / "web" / name, docs / name)
    (docs / ".nojekyll").touch()
    fields = ["company", "title", "category", "location", "period", "duration", "posted_at", "first_seen_at", "last_seen_at", "url"]
    with (docs / "internships.csv").open("w", newline="") as output:
        writer = csv.DictWriter(output, fields)
        writer.writeheader()
        for job in jobs:
            values = {key: job.get(key) or "" for key in fields}
            # Defuse spreadsheet formula interpretation of external text.
            writer.writerow({key: "'" + value if value.lstrip().startswith(("=", "+", "-", "@")) else value for key, value in values.items()})
    feed = ET.Element("feed", xmlns="http://www.w3.org/2005/Atom")
    ET.SubElement(feed, "title").text = "Singapore Internship Tracker"
    ET.SubElement(feed, "id").text = "urn:singapore-internship-tracker"
    ET.SubElement(feed, "updated").text = state["last_attempt_at"] or "1970-01-01T00:00:00Z"
    author = ET.SubElement(feed, "author")
    ET.SubElement(author, "name").text = "Singapore Internship Tracker"
    for job in jobs[:100]:
        entry = ET.SubElement(feed, "entry")
        ET.SubElement(entry, "id").text = "urn:sg-intern:" + job["id"]
        ET.SubElement(entry, "title").text = f"{job['company']} · {job['title']}"
        ET.SubElement(entry, "link", href=job["url"])
        ET.SubElement(entry, "updated").text = job["first_seen_at"]
        ET.SubElement(entry, "summary").text = f"{job['location']} · Period: {job.get('period') or 'Not stated'}"
    ET.ElementTree(feed).write(docs / "feed.xml", encoding="utf-8", xml_declaration=True)
