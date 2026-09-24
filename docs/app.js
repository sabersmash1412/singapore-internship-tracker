"use strict";
const data = JSON.parse(document.getElementById("tracker-data").textContent);
const $ = id => document.getElementById(id);
const date = value => value ? new Date(value).toLocaleDateString("en-SG", {day:"numeric",month:"short",year:"numeric",timeZone:"Asia/Singapore"}) : "Not stated";
const node = (tag, text, className) => { const el = document.createElement(tag); el.textContent = text; if (className) el.className = className; return el; };
$("total").textContent = data.jobs.length;
$("companies").textContent = new Set(data.jobs.map(j => j.company)).size;
$("boards").textContent = data.sources.length;
const stale = !data.updated_at || Date.now() - new Date(data.updated_at).getTime() > 6 * 3600000;
$("updated").textContent = data.updated_at ? `Last collection · ${new Date(data.updated_at).toLocaleString("en-SG", {timeZone:"Asia/Singapore"})} SGT${stale ? " · Data may be stale" : ""}` : "Awaiting the first collection";
if (stale) $("updated").classList.add("warning");
for (const key of ["category", "company", "period"]) {
  [...new Set(data.jobs.map(j => j[key] || "Not stated"))].sort().forEach(value => {
    const option = node("option", value); option.value = value; $(key).append(option);
  });
}
function render() {
  const query = $("search").value.trim().toLowerCase();
  const jobs = data.jobs.filter(j => (!query || [j.company,j.title,j.category,j.period].join(" ").toLowerCase().includes(query)) && ["category","company","period"].every(key => !$(key).value || (j[key] || "Not stated") === $(key).value));
  if ($("sort").value === "company") jobs.sort((a,b) => a.company.localeCompare(b.company) || a.title.localeCompare(b.title));
  $("jobs").replaceChildren();
  $("result-count").textContent = `${jobs.length} ${jobs.length === 1 ? "opportunity" : "opportunities"}`;
  $("empty").hidden = jobs.length !== 0;
  jobs.forEach(job => {
    const card = node("article", "", "job");
    const identity = node("div", "", "identity");
    identity.append(node("div", job.company.slice(0,2).toUpperCase(), "company-icon"));
    const body = node("div", "", "job-body");
    body.append(node("p", job.company, "company-name"), node("h3", job.title));
    const tags = node("div", "", "tags");
    [job.category, job.period || "Period not stated", job.duration].filter(Boolean).forEach(t => tags.append(node("span", t)));
    body.append(tags, node("p", `${job.location} · First seen ${date(job.first_seen_at)}`, "meta"));
    const details = node("details", "", "details");
    details.append(node("summary", "Dates & source details"));
    details.append(node("p", `Employer posted: ${date(job.posted_at)} · Last seen: ${date(job.last_seen_at)}`));
    if (job.period_evidence) details.append(node("p", `Period evidence: ${job.period_evidence}`));
    if (job.duration_evidence) details.append(node("p", `Duration evidence: ${job.duration_evidence}`));
    details.append(node("p", "Eligibility, allowance and deadlines: check the employer’s posting."));
    const source = data.sources.find(s => s.board === job.board);
    if (!source?.complete) details.append(node("p", "Latest source check was incomplete; this role is retained from an earlier check.", "warning"));
    body.append(details);
    identity.append(body);
    const apply = node("a", "View role ↗", "apply");
    if (job.url.startsWith("https://")) apply.href = job.url;
    apply.target = "_blank"; apply.rel = "noopener noreferrer";
    apply.setAttribute("aria-label", `View ${job.title} at ${job.company}`);
    card.append(identity, apply); $("jobs").append(card);
  });
}
for (const id of ["search","category","company","period","sort"]) $(id).addEventListener("input", render);
$("reset").addEventListener("click", () => { ["search","category","company","period"].forEach(id => $(id).value = ""); render(); });
data.sources.forEach(source => {
  const row = node("div", "", "source-row");
  row.append(node("span", source.board), node("span", source.complete ? `${source.matched} matches · Checked` : "Incomplete check", source.complete ? "ok" : "warning"));
  $("sources").append(row);
  if (source.error) $("sources").append(node("p", source.error, "source-error"));
  if (source.warnings.length) $("sources").append(node("p", `${source.warnings.length} posting details unavailable`, "source-error"));
});
render();
