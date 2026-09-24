# Employer expansion audit — 24 September 2026

Collected at 2026-09-24T09:56:59.615201+00:00 from public employer endpoints.

- Expanded from 20 to 64 registered feeds: 44 added.
- All 64 sources completed without errors or detail warnings in the local full collection.
- Added feeds returned 41 matching Singapore technical internships; the published snapshot contains 458 open listings across 30 employer/agency labels.
- A source with zero matching internships is still monitored. This is not a claim that 64 companies currently offer internships, nor complete coverage of Singapore employers.
- The Public Service feed is a shared board; individual hiring agencies are preserved on listings.

## Added coverage

| Employer / shared board | Platform | Matching internships |
| --- | --- | ---: |
| [Agoda](https://job-boards.greenhouse.io/agoda) | greenhouse | 0 |
| [Airwallex](https://jobs.ashbyhq.com/airwallex) | ashby | 2 |
| [Bifrost](https://jobs.ashbyhq.com/bifrost) | ashby | 0 |
| [Binance](https://jobs.lever.co/binance) | lever | 0 |
| [BitGo](https://job-boards.greenhouse.io/bitgo) | greenhouse | 0 |
| [Bosch](https://careers.smartrecruiters.com/BoschGroup) | smartrecruiters | 2 |
| [Cantina](https://jobs.ashbyhq.com/cantina) | ashby | 1 |
| [Carousell Group](https://careers.smartrecruiters.com/CarousellGroup) | smartrecruiters | 1 |
| [ClickHouse](https://jobs.ashbyhq.com/clickhouse) | ashby | 0 |
| [Cohere](https://jobs.ashbyhq.com/cohere) | ashby | 0 |
| [Coinbase](https://job-boards.greenhouse.io/coinbase) | greenhouse | 0 |
| [Continental](https://careers.smartrecruiters.com/Continental) | smartrecruiters | 0 |
| [Crypto.com](https://jobs.lever.co/crypto) | lever | 0 |
| [Databricks](https://job-boards.greenhouse.io/databricks) | greenhouse | 0 |
| [Datadog](https://job-boards.greenhouse.io/datadog) | greenhouse | 0 |
| [Elastic](https://job-boards.greenhouse.io/elastic) | greenhouse | 0 |
| [ElevenLabs](https://jobs.ashbyhq.com/elevenlabs) | ashby | 0 |
| [Figma](https://job-boards.greenhouse.io/figma) | greenhouse | 0 |
| [Gemini](https://job-boards.greenhouse.io/gemini) | greenhouse | 0 |
| [Jane Street](https://job-boards.greenhouse.io/janestreet) | greenhouse | 0 |
| [Jump Trading](https://job-boards.greenhouse.io/jumptrading) | greenhouse | 6 |
| [k-ID](https://jobs.ashbyhq.com/k-ID) | ashby | 0 |
| [Lalamove](https://jobs.lever.co/lalamove) | lever | 0 |
| [Lumilens](https://jobs.ashbyhq.com/lumilens) | ashby | 0 |
| [MongoDB](https://job-boards.greenhouse.io/mongodb) | greenhouse | 0 |
| [NCS](https://careers.smartrecruiters.com/NCS3) | smartrecruiters | 19 |
| [Nium](https://jobs.lever.co/nium) | lever | 0 |
| [OKX](https://job-boards.greenhouse.io/okx) | greenhouse | 0 |
| [OpenAI](https://jobs.ashbyhq.com/openai) | ashby | 0 |
| [Palantir Technologies](https://jobs.lever.co/palantir) | lever | 1 |
| [Portcast](https://jobs.lever.co/portcast) | lever | 1 |
| [Renesas Electronics](https://careers.smartrecruiters.com/RenesasElectronics) | smartrecruiters | 0 |
| [Rubrik](https://job-boards.greenhouse.io/rubrik) | greenhouse | 0 |
| [ServiceNow](https://careers.smartrecruiters.com/ServiceNow) | smartrecruiters | 0 |
| [SimplifyNext](https://job-boards.greenhouse.io/simplifynext) | greenhouse | 0 |
| [Singapore Public Service](https://sggovterp.wd102.myworkdayjobs.com/PublicServiceCareers) | workday | 4 |
| [Stripe](https://job-boards.greenhouse.io/stripe) | greenhouse | 1 |
| [Supabase](https://jobs.ashbyhq.com/supabase) | ashby | 0 |
| [Thunes](https://job-boards.greenhouse.io/thunes) | greenhouse | 0 |
| [Tower Research Capital](https://job-boards.greenhouse.io/towerresearchcapital) | greenhouse | 3 |
| [Trust Bank](https://job-boards.greenhouse.io/trustbank) | greenhouse | 0 |
| [Verkada](https://job-boards.greenhouse.io/verkada) | greenhouse | 0 |
| [Western Digital](https://careers.smartrecruiters.com/WesternDigital) | smartrecruiters | 0 |
| [Wise](https://careers.smartrecruiters.com/Wise) | smartrecruiters | 0 |

## Review and limitations

All selected boards returned Singapore-location evidence, even when they had no qualifying internships. Public ATS records provide stable identities and application links; no applicant data, login credentials or aggregator listings are collected.

Reviewed all newly matched titles. Checked NCS descriptions for ambiguous AI, HR, learning-content, legal and presales roles. Excluded People & Culture roles attached to AI teams, business strategy, AI strategy/planning and learning-content development. Retained hands-on AI solution engineering, workflow automation and technical roles. Classification remains heuristic and may omit generic research/engineering titles.

Ashby primary/secondary country evidence and structured internship status are covered by regression tests, including unlisted postings, malformed responses and duplicate IDs. Shared Workday agency attribution and missing detail failures are also tested. Intake ranges using “till” now work in both extraction and older-period display. The complete offline suite passes 81 tests.

Candidates with empty feeds or no explicit Singapore jobs were not added merely to increase the count. Ninja Van's tested Lever feed had a malformed location record and remains deferred. Workable candidates, including Funding Societies, require a separately validated collector before inclusion. Open Government Products and Activate Interactive use other career-site formats requiring additional work. Tested slugs returning 404 do not establish that the employer lacks internships. No formal legal SME classification was verified.

Local collection success does not guarantee future endpoint stability or GitHub runner connectivity. Existing source-health checks and failed-run notifications remain enabled. The 30-minute external schedule is unchanged.
