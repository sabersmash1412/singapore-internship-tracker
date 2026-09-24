# Maintaining the Singapore internship list

The README is the primary publication. Python 3.11+ and its standard library are the only local requirements.

## Run locally

```sh
python3 -m unittest discover -s tests -v
python3 run.py update
```

`update` reads employer feeds, updates history, and regenerates README.md, data/jobs.json and data/internships.csv. `python3 run.py render` regenerates them from saved history without fetching. Do not manually edit the README section between the internship markers; text outside those markers is preserved.

## GitHub automation

Push changes to `main`, then use **Actions → Refresh internships → Run workflow**. The existing refresh.yml workflow requests a run every 30 minutes and commits the README and data back to the repository. Schedules can be delayed: the README states the actual collection time.

GitHub Pages is not needed. If a website was previously deployed, removing the deployment workflow does not unpublish it; it can be unpublished separately from repository Settings → Pages.

Only `contents: write` permission is requested. No secrets are needed. Branch protection or organization policy may require adapting the bot commit process. Concurrent scheduled writers are serialized; non-fast-forward pushes fail rather than overwrite new commits.

## Add employers

Edit data/companies.json. Each entry needs `name`, `platform`, `slug`, and `careers_url`. Supported platforms: Greenhouse, Lever, SmartRecruiters, ByteDance/TikTok public supplier search, Workday, Shopee, Sea and GovTech. See existing registry entries for each platform’s required `api_base` or `website_path` fields, and [SOURCES.md](SOURCES.md) for provenance. Confirm the official feed token and run the collector before submitting a change. A board with zero matches can still be healthy.

Keep public job URLs as application links. Do not submit credentials, private student-portal data or personal applicant information. Removing a board from the registry does not remove its historical listings; retiring a source needs an explicit history migration.

## Data and limitations

- data/state.json retains lifecycle history; do not replace it with an empty file during normal updates.
- Source IDs prevent repeat rows across runs. Cross-platform duplicate detection is not implemented; distinct requisitions remain distinct.
- Classification uses titles and explicit employer internship/role metadata. Broad programme names can still be missed. Period extraction is deliberately limited.
- Full descriptions are not persisted, only selected metadata and brief evidence excerpts.
- Eligibility, allowance and application deadlines are not currently extracted.
- An all-source failure preserves the previous README/data and fails the run. Partial failures are shown in README source health.
- Do not run simultaneous local updates. Tests use temporary directories.

## Structure

- tracker/sources.py — public feeds and pagination
- tracker/regional.py — Singapore employer connectors and completeness checks
- tracker/classify.py — Singapore, technical role and period classification
- tracker/state.py — history and closure rules
- tracker/publish.py — README table and CSV/JSON generation
- tests/ — classification, lifecycle, source and publication checks

Next priority: broaden multinational, semiconductor and startup coverage, and measure recall against a manually reviewed sample. A board being monitored does not imply that it currently has matching roles.
