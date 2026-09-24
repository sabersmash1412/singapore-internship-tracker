# Employer coverage

The tracker reads official employer sources. Checked on 24 September 2026. A monitored employer may have no matching open technical internships. The README’s source-health table reports each actual run.

| Employer | Official careers source | Collection method |
| --- | --- | --- |
| TikTok | [Life at TikTok](https://lifeattiktok.com/search) | Public supplier API, live Singapore filter and structured internship type |
| ByteDance | [Join ByteDance](https://joinbytedance.com/search) | Public supplier API, English website header, live Singapore filter |
| Shopee | [Shopee Careers](https://careers.shopee.sg/jobs) | Public Work at Sea ATS, live location and employment metadata |
| Sea | [Sea Careers](https://career.sea.com/jobs) | Official site job-list API and shared ATS metadata |
| GovTech | [Internship projects](https://internships.tech.gov.sg/projects) | Public server-rendered internship catalogue, technical role groups and filled status |
| DBS | [DBS Careers](https://dbs.wd3.myworkdayjobs.com/DBS_Careers) | Workday search and posting details |
| OCBC | [OCBC Careers](https://ocbc.wd102.myworkdayjobs.com/External) | Workday search and posting details |
| UOB | [UOB Careers](https://uobgroup.wd3.myworkdayjobs.com/UOBExternal) | Workday search and posting details |
| Grab | [Grab Careers](https://careers.smartrecruiters.com/Grab) | SmartRecruiters public postings |
| ShopBack | [ShopBack Careers](https://jobs.lever.co/shopback-2) | Lever public postings |
| Temus | [Temus Careers](https://job-boards.greenhouse.io/temus) | Greenhouse public job board |
| Applied Materials | [Workday postings](https://amat.wd1.myworkdayjobs.com/External) | Public Workday search, live Singapore country facet and full posting details |
| GlobalFoundries | [Workday postings](https://globalfoundries.wd1.myworkdayjobs.com/External) | Public Workday search, nested Singapore country facet and full posting details |
| NXP | [NXP careers](https://www.nxp.com/company/about-nxp/careers:CAREERS) → [Workday](https://nxp.wd3.myworkdayjobs.com/careers) | Public Workday search, live Singapore country facet and full posting details |
| DRW | [DRW Careers](https://job-boards.greenhouse.io/drweng) | Greenhouse public job board |

## Provenance and scope

- The DBS, OCBC and UOB board links were followed from their official internship/early-careers pages. GovTech’s [internship page](https://www.tech.gov.sg/careers/students-and-graduates/internships/) links to the project catalogue.
- TikTok/ByteDance and Sea/Shopee requests reproduce public job searches discovered in the careers sites’ public JavaScript. No authentication, applicant data or private APIs are used. These are website endpoints and their schemas may change.
- TikTok and ByteDance are tracked separately. Stable source IDs deduplicate each board; cross-brand requisitions are not automatically merged.
- Shopee’s feed can carry Monee roles. The Shopee connector retains the Shopee entity rather than labelling Monee jobs as Shopee. Sea’s own public careers feed covers its listed teams.
- GovTech is a project catalogue rather than conventional requisitions. Only technical role groups are included. Filled projects are excluded. Work locations marked “Others” are excluded unless independently supported by explicit Singapore location evidence. Known Singapore postal addresses and Punggol Digital District provide local address evidence. The application deadline is read from the official programme page on each collection, with Singapore time. Intake eligibility must still be checked on the employer page.
- Workday detail country fields resolve office names that do not say “Singapore.” Detail failures make the board incomplete so previous listings cannot be closed from missing evidence. Later pages may report total=0; pagination uses the first-page total and checks unique IDs.
- Pagination caps, malformed records, changing totals and repeated pages fail completeness. A partial response may contribute valid new roles but never closes roles merely because they are absent.
- Older advertised periods are separated into a collapsed README table. Explicit month ranges and half-years use their end month; seasonal display hints use May/August/November for Spring/Summer/Fall and the following March for Winter. These conventions never close jobs. Multiple periods remain in the main table if any is current, future or unrecognized.
- HR business-partner and commercial-support titles are excluded. Administrative project-management roles cannot qualify solely through a parenthesized AI/data team name; IT project-management and actual data-analytics roles remain eligible. Classification is heuristic: product/design and business analytics roles can appear alongside engineering.
- At the [24 September audit](audits/2026-09-24.md), GovTech’s official page stated applications close **30 September 2026 at 12pm**. The tracker now closes these rows at that deadline on the first successful refresh, even if `filled=false` remains in the catalogue. Missing or ambiguous programme deadlines make the source incomplete; previously recorded deadlines still apply. A new explicit future deadline can reopen listings. No deadlines are inferred from intake periods.

## Validation

Offline tests cover pagination, malformed/error responses, structured internship status, Singapore location resolution, filled projects, source failures, lifecycle transitions and deterministic README generation. A successful local collection does not guarantee a GitHub-hosted runner can reach every employer; inspect source health after the scheduled workflow runs.

## Semiconductor expansion — 24 September 2026

Applied Materials, GlobalFoundries and NXP are monitored through public Workday postings. Singapore country IDs are resolved from current metadata rather than hardcoded; each posting still needs its own Singapore location evidence. NXP currently has no matching Singapore internships. General graduate jobs and nontechnical internships are excluded.

Applied Materials' [Singapore internship programme](https://www.appliedmaterials.com/sg/en/careers/university-recruiting-programs.html) and [public job site](https://jobs.appliedmaterials.com/location/singapore-jobs/95/1880251/2) establish programme and location context. GlobalFoundries' [Singapore university internship](https://globalfoundries.wd1.myworkdayjobs.com/en-US/External/job/University-Intern---Year-2026_JR-2503754) links back to its corporate careers information. NXP's corporate page links directly to its Workday board.

Specific hardware terms now include hybrid bonding, process integration, PVD, CVD, 3DIC, CMOS, testchip, ESD device and silicon photonics. Generic titles such as “College Intern” or “University Intern” remain outside automatic matching even if a description may contain technical work. Semiconductor coverage is consequently conservative and incomplete; employment at a chip company alone does not qualify a role. Micron was investigated but is not added in this batch.

Validation: all 15 sources completed successfully in the local live collection. Applied Materials returned 12 matching internships, GlobalFoundries 12 and NXP 0. The resulting 373 active listings include 121 GovTech projects with recorded deadlines. All 50 offline tests pass, including an in-memory cutoff simulation that removes all 121 GovTech projects from active exports while preserving closed history. New boards still need a GitHub-hosted refresh to confirm runner connectivity.
