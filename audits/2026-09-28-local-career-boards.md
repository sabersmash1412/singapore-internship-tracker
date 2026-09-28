# Micron repair and local career-board audit — 28 September 2026

Collection completed at 2026-09-28T06:59:26.525148+00:00.

- **152 registered sources**: added Singtel, ST Engineering and Temasek.
- **15 new-source technical internships**, with 516 open listings overall (including older advertised periods).
- Micron completed with **82 internship records**, of which **23** match the technical Singapore scope.
- Full collection: **273 seconds**, four workers; **152/152 healthy**.
- All **102 offline tests** pass; README and exports are reproducible. No schedule or notification changes.

## Micron diagnosis and repair

A regular facilities record, JR106128, appeared in the broad `intern` keyword search with only `bulletFields`, no title or external path. Exact-ID search reproduced the malformed result and identified the regular worker type. The collector correctly refused to infer closures from that result.

The repaired query resolves the official `Interns` job-family category from live metadata and combines it with the existing Singapore site facets. It does not hardcode facet IDs or ignore malformed rows. Every retained Micron role still discoverable through exact-ID search was present in this category. JR97726 was absent from both category and exact-ID searches, so the normal two-complete-run absence rule applies. Existing identifiers and first-seen dates remain unchanged. Missing category metadata or malformed internship records still fail completeness. Internships classified outside the employer's Interns category may be missed.

## New public career pages

| Employer | Matching internships | Scope |
| --- | ---: | --- |
| Singtel | 1 | Official public career search and posting details |
| ST Engineering | 0 | Official public career search and posting details |
| Temasek | 14 | Official public career search and posting details |

The collector uses explicit page ranges/totals and the site's date-sort controls, checks unique posting IDs, validates detail titles, and extracts full descriptions and publication microdata. An explicit no-results notice overrides unrelated recent-job suggestions. Singapore country-code location cells are supported. Singtel is limited to the Singtel department; NCS is already monitored separately. Employer-branding roles attached to AI teams are excluded.

ST Engineering currently returns no qualifying internship-title listings; its public board is monitored for future entries, not represented as currently hiring interns. Some internships may instead be distributed through schools or separate programmes.

## Other employers investigated

- DSTA's [official internship page](https://www.dsta.gov.sg/join-us) directs university/polytechnic students to institution project listings. No private student portal or applicant data is accessed.
- GIC's [internship programme](https://gic.careers/programmes/gic-internship-programme/) includes a Technology pathway and links to an application chatbot. Its separate general-careers search returned no internship titles. It is not counted as an automated student-programme feed.
- [A*STAR careers](https://careers.a-star.edu.sg/) uses a different dynamic search interface. The advertised RSS keyword feed returned exactly 20 broad matches, no internship titles, and no completeness/pagination metadata. A previously indexed Uni Jan 2027 research attachment page was explicitly unavailable when opened. These were not converted into invented active technical roles.

The main table retains `-` for unknown fields and arrows for consecutive repeated employers. Public availability and classification remain conservative; a successful local run does not guarantee future endpoint availability or GitHub runner connectivity.
