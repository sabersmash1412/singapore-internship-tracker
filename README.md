# Singapore Internship Tracker

A year-round tracker for technical internships located in Singapore. Built from scratch with Python's standard library and a static HTML/CSS/JavaScript dashboard. Python 3.11+; no dependencies, database, API keys, or accounts needed locally.

## Run locally

```sh
python3 -m unittest discover -s tests -v
python3 run.py update
python3 run.py serve
```

Open http://localhost:8000. Stop with Ctrl+C. `python3 run.py render` rebuilds the site from saved data without network requests. Commands work from any directory when given the absolute path to `run.py`.

## Enable your GitHub deployment

The existing remote is `https://github.com/sabersmash1412/singapore-internship-tracker.git`.

1. Review the local files and commit/push the project to `main` (commands below).
2. In the GitHub repository, open **Settings → Pages → Build and deployment → Source**, and select **GitHub Actions**.
3. In **Actions**, open **Refresh and publish**, then **Run workflow** on `main`.
4. The workflow fetches jobs, saves history to the repository, and deploys the dashboard. Its deployment step provides the site URL. Expected URL: https://sabersmash1412.github.io/singapore-internship-tracker/.
5. After the first successful deployment, the workflow requests updates every 30 minutes. GitHub scheduled runs may be delayed; check the visible last-collection timestamp.

```sh
git add .
git commit -m "Build initial Singapore internship tracker"
git branch -M main
git push -u origin main
```

The workflow declares the permissions it needs. Repository/organization policies or protected branches may still prevent the data commit; inspect the failed Actions step rather than disabling branch protection blindly. No service secrets are required.

## Initial coverage

| Employer | Public feed | Official board |
| --- | --- | --- |
| Grab | SmartRecruiters | https://careers.smartrecruiters.com/Grab |
| ShopBack | Lever | https://jobs.lever.co/shopback-2 |
| Temus | Greenhouse | https://job-boards.greenhouse.io/temus |
| DRW | Greenhouse | https://job-boards.greenhouse.io/drweng |

Add a board to `data/companies.json` with `name`, `platform`, `slug`, and `careers_url`. Supported platforms: `greenhouse`, `lever`, `smartrecruiters`. Adding a company does not imply that it has matching internships. Validate the official board token before adding it. Removed boards' historical records are retained; retiring a source needs an explicit history migration.

## Data policy and limitations

- Singapore is matched from the job's location or structured country, never the employer's headquarters or description. Generic remote/APAC jobs are excluded.
- Internship and technical-role matching currently use titles. Broad programme titles and unrecognised terminology can be missed.
- Periods are quoted from explicit title/description evidence. A bare year never becomes a season. Extraction is deliberately limited; unknown periods remain visible.
- Posting dates use employer publication fields when available. Lever creation timestamps and Greenhouse update timestamps are not presented as publication dates. First-seen dates are tracked separately.
- A job closes after two complete board checks fail to return it in scope. Incomplete/error responses cannot close jobs. No automatic applications or messages are sent.
- Identity uses platform + board + source posting ID. Separate requisitions stay separate; cross-platform duplicates are not yet merged.
- Only selected metadata and short evidence excerpts are persisted, not full descriptions. Eligibility, deadlines, salaries and inferred university credit compatibility are not extracted in this release.
- All-source failure preserves the previous data/site and fails the run. Partial failures remain visible in source status; the site flags collection timestamps older than six hours.
- State is committed as readable JSON. Do not run multiple local `update` processes simultaneously. Actions serialises scheduled writers and refuses a non-fast-forward push.
- Open means present in the feed, not a guarantee that the employer is still accepting applications. Old start windows are retained if the role remains listed.

## Files

`tracker/sources.py`: connectors and pagination. `tracker/classify.py`: Singapore/role/period rules. `tracker/state.py`: lifecycle and history. `tracker/publish.py`: dashboard and exports. `web/`: editable presentation. `data/state.json`: collected history. `docs/`: generated site (do not edit directly).

Outputs: `docs/index.html`, `docs/api/jobs.json`, `docs/internships.csv`, and the Atom subscription feed `docs/feed.xml`.

## Next milestones

1. Expand verified coverage to 30–50 employers. Audit TikTok/ByteDance, Sea/Shopee, GovTech, banks and semiconductor employers; add connectors only after checking actual feeds.
2. Broaden programme-title detection using labelled examples, then parse start windows/duration more systematically.
3. Add Telegram alerts with a persistent delivery ledger after deployment is stable.
4. Add explicit eligibility, allowance and deadline evidence; do not infer these from company identity.

Architecture informed by a review of [the US internship tracker](https://github.com/zshah101/Automated-List-Of-Summer-2027-and-Fall-2026-Tech-Internships); this implementation is new code.
