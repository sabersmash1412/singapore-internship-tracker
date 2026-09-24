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
| DRW | [DRW Careers](https://job-boards.greenhouse.io/drweng) | Greenhouse public job board |

## Provenance and scope

- The DBS, OCBC and UOB board links were followed from their official internship/early-careers pages. GovTech’s [internship page](https://www.tech.gov.sg/careers/students-and-graduates/internships/) links to the project catalogue.
- TikTok/ByteDance and Sea/Shopee requests reproduce public job searches discovered in the careers sites’ public JavaScript. No authentication, applicant data or private APIs are used. These are website endpoints and their schemas may change.
- TikTok and ByteDance are tracked separately. Stable source IDs deduplicate each board; cross-brand requisitions are not automatically merged.
- Shopee’s feed can carry Monee roles. The Shopee connector retains the Shopee entity rather than labelling Monee jobs as Shopee. Sea’s own public careers feed covers its listed teams.
- GovTech is a project catalogue rather than conventional requisitions. Only technical role groups are included. Filled projects are excluded. Work locations marked “Others” are excluded unless independently supported by explicit Singapore location evidence. Known Singapore postal addresses and Punggol Digital District provide local address evidence. Application dates and intake eligibility must still be checked on the employer page.
- Workday detail country fields resolve office names that do not say “Singapore.” Detail failures make the board incomplete so previous listings cannot be closed from missing evidence. Later pages may report total=0; pagination uses the first-page total and checks unique IDs.
- Pagination caps, malformed records, changing totals and repeated pages fail completeness. A partial response may contribute valid new roles but never closes roles merely because they are absent.
- Listings still advertised with prior-calendar-year periods are explicitly flagged in the README; they are not silently relabelled as a new intake. Multiple stated periods are preserved.

## Validation

Offline tests cover pagination, malformed/error responses, structured internship status, Singapore location resolution, filled projects, source failures, lifecycle transitions and deterministic README generation. A successful local collection does not guarantee a GitHub-hosted runner can reach every employer; inspect source health after the scheduled workflow runs.
