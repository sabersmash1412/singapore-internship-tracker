# Post-expansion listing audit — 24 September 2026

Reviewed 30 published listings across all 17 employers with active roles: one per employer, plus a second from 13 employers, emphasizing newly added sources. This is a purposive sample, not a statistical accuracy estimate. DBS, NXP and NVIDIA have no matching roles.

## Results

- All 30 IDs remained in the fresh official collection. Reviewed role descriptions or structured GovTech role data, Singapore location evidence, internship status, posted-date metadata and extracted intake evidence. No confirmed scope errors were found in this sample. Analytics, technical operations and technology project roles remain within scope.
- All 30 official posting URLs returned HTTP 200. This verifies reachability only: some pages are JavaScript shells. No application submission or acceptance test was performed.
- Found seven omitted technical requisitions: three Shopee Business Intelligence internships, two Shopee LLM engineering/product internships, one TikTok LLM product internship and one Micron silicon-design-validation internship. Added narrow title rules after reviewing their duties. Finance/accounting roles mentioning Business Intelligence only as a team name remain excluded. One recovered BI role advertises Summer 2026 and belongs in the older-period section.
- Fixed Amazon's Jan–Jun 2027 intake being discarded when a graduation requirement and a separate availability bullet were flattened into one text block. Graduation dates remain excluded, and month-range hyphens remain intact.
- Before changes, 405 active records had no duplicate IDs or application URLs. Six company/title groups had two distinct requisitions each. Retain separate requisitions; identical titles or even identical descriptions alone do not prove the employer intended one vacancy. The two newly recovered Spring 2027 BI postings also have distinct employer IDs and URLs.
- Conservative omissions remain, including generic engineering/product titles and technical work hidden behind finance or programme-manager titles. Apple fiscal-year wording and its broad 2027 programme title are not converted into an inferred intake. Unknown table fields remain `-`.

## Lifecycle checks

Regression tests cover two complete misses before closure, reopening when a role reappears, resetting misses during source outages, failed-detail preservation, explicit deadline closure and excluding closed records from active exports. Older intake dates only change presentation, not availability. These are controlled tests, not proof that an employer's catalogue instantly reflects closed applications.

## Reviewed sample

All decisions are keep; the Amazon intake correction is noted below. Employer links provide the review evidence.

| # | Employer | Official listing | Review finding |
| --- | --- | --- | --- |
| 1 | AMD | [IC Design Exploration Intern](<https://careers.amd.com/students/jobs/76892>) | IC design, verification and silicon validation; January 2027 start with alternative end dates. |
| 2 | Amazon | [Program Manager Intern, APAC Data Center Delivery Operations](<https://www.amazon.jobs/en/jobs/10529692/program-manager-intern-apac-data-center-delivery-operations>) | Data architecture, validation and analytics; fix missed Jan–Jun 2027 intake after a graduation bullet. |
| 3 | Apple | [2027 Apple Internship - Information Systems and Technology](<https://jobs.apple.com/en-us/details/200675982-3278/2027-apple-internship-information-systems-and-technology>) | Software, cloud and data engineering programme; title states 2027 but no precise intake extracted. |
| 4 | Applied Materials | [College Intern - GT Indigo Inter-Die Gapfill Process and Integration for 3DIC](<https://amat.wd1.myworkdayjobs.com/External/job/SingaporeSGP/College-Intern---GT-Indigo-Inter-Die-Gapfill-Process-and-Integration-for-3DIC_R2626651>) | Thin-film deposition experiments for semiconductor packaging. |
| 5 | ByteDance | [Large Model Algorithm Engineer Intern (Data Model) - 2026 Start (PHD)](<https://joinbytedance.com/search/7530952054316910866>) | Large-model reasoning and algorithm development; 2026 start. |
| 6 | DRW | [Software Developer Intern (C++)](<https://job-boards.greenhouse.io/drweng/jobs/8014910>) | C++ trading and risk software development. |
| 7 | GlobalFoundries | [ESD Device Design Engineer Intern (Jan-Jun 2027)](<https://globalfoundries.wd1.myworkdayjobs.com/External/job/SGP---Woodlands/ESD-Device-Design-Engineer-Intern--Jan-Jun-2027-_JR-2604348>) | ESD device experiments and IC protection design; Jan–Jun 2027. |
| 8 | GovTech | [Tech – Data Scientist: Audit Automation](<https://internships.tech.gov.sg/projects/data-scientist/audit-automation>) | Data science and engineering applied to internal audit; structured technical role and Singapore postal address. |
| 9 | Grab | [Intern, Analytics & Projects, GrabMart](<https://jobs.smartrecruiters.com/Grab/744000147416979>) | SQL queries, reporting and business analytics; January 2027 start. |
| 10 | Micron | [AI, Data & Digital Solutions Internship (Singapore)](<https://micron.wd1.myworkdayjobs.com/External/job/Fab-10NX-Singapore/AI--Data---Digital-Solutions-Internship--Singapore-_JR106776>) | AI, software, automation and analytics programme at Singapore sites; Jan–Jun 2027. |
| 11 | OCBC | [Internship: Global Commercial Banking, GWB Data Analytics [Jan to May 2027]](<https://ocbc.wd102.myworkdayjobs.com/External/job/OCBC-Singapore/Internship--Global-Commercial-Banking--GWB-Data-Analytics--Jan-to-May-2027-_JR00011058>) | Power BI, data preparation and AI research; Jan–May 2027. |
| 12 | Sea | [Backend Engineer Intern](<https://career.sea.com/position/J02044564>) | Backend application development and testing; January 2027 start. |
| 13 | ShopBack | [Operations Automation Engineer Intern](<https://jobs.lever.co/shopback-2/0b3627b7-0c1a-46da-bc3d-699f8d5ca9e5>) | Python automation and prototypes; H2 2026. |
| 14 | Shopee | [Data Analyst Intern - Regional Marketing Analytics, Regional Brand & Growth Marketing (Spring 2027)](<https://careers.shopee.sg/job-detail/J00004459/1>) | Python/SQL analytics and reporting automation; Spring 2027. |
| 15 | Temus | [AI/Data Intern (May - Dec 2026)](<https://job-boards.greenhouse.io/temus/jobs/5169522008>) | Machine learning experiments and data pipelines; May–Dec 2026. |
| 16 | TikTok | [Data Analyst Project Intern (Safety Model Operations) - 2026 Start (BS/MS）](<https://lifeattiktok.com/search/7504596715490019592>) | Dashboards and SQL/Python analysis; 2026 start. |
| 17 | UOB | [GenAI and Data Analytics Intern (Jan - Dec 2027)](<https://uobgroup.wd3.myworkdayjobs.com/UOBExternal/job/Central-Region-City-Area/GenAI-and-Data-Analytics-Intern--Jan---Dec-2027-_JR96223>) | GenAI solutions, data marts and analytics; Jan–Dec 2027. |
| 18 | Micron | [Intern, Photo Manufacturing Data Analytics and AI](<https://micron.wd1.myworkdayjobs.com/External/job/Fab-10NX-Singapore/Intern--Photo-Manufacturing-Data-Analytics-and-AI_JR112194>) | Manufacturing analytical models and dashboards; Jan–May 2027. |
| 19 | AMD | [Advanced Packaging Optical Characterization Intern](<https://careers.amd.com/students/jobs/92029>) | Optical measurements, instrument automation and engineering analysis; January 2027 start. |
| 20 | Apple | [Information Security Internship Program (FY27 Summer Intake)](<https://jobs.apple.com/en-us/details/200684585-3278/information-security-internship-program-fy27-summer-intake>) | Cybersecurity incident response, analytics and software development; fiscal-year summer wording left unparsed. |
| 21 | Amazon | [Software Developer Intern, Field Innovation, Security Search and Observability (SSO)](<https://www.amazon.jobs/en/jobs/10544261/software-developer-intern-field-innovation-security-search-and-observability-sso>) | Software engineering and cloud services; Jan–June 2027. |
| 22 | GlobalFoundries | [2H University Intern, AI-Driven Process Intern (Advanced Process Control)](<https://globalfoundries.wd1.myworkdayjobs.com/External/job/SGP---Woodlands/XMLNAME-2H-University-Intern--AI-Driven-Process-Intern--Advanced-Process-Control-_JR-2502691>) | AI agents, APIs and engineering automation; June 2026 onwards remains source-listed, not evidence of closure. |
| 23 | Applied Materials | [Technology Development Engineer – Hybrid Bonding & Advanced Packaging (Internship)](<https://amat.wd1.myworkdayjobs.com/External/job/SingaporeSGP/Technology-Development-Engineer---Hybrid-Bonding---Advanced-Packaging--Internship-_R2626901>) | Hybrid bonding, process integration and advanced chip packaging. |
| 24 | GovTech | [Tech – Software Engineer: CIOO Applications & Products](<https://internships.tech.gov.sg/projects/software-engineer/cioo-applications-and-products-cioo>) | Structured Software Engineer project; internal products and productivity tools, Singapore postal address. |
| 25 | TikTok | [AI Model and Agent Operation Project Intern (Business Integrity) - 2027 Start](<https://lifeattiktok.com/search/7685635965980821813>) | AI model evaluation, machine-executable policies and operational automation; 2027 start. |
| 26 | ByteDance | [Machine Learning Engineer Intern (Global E-Commerce, Search) - 2027 Start](<https://joinbytedance.com/search/7686120054081014069>) | Multimodal search and ranking algorithms; 2027 start. |
| 27 | Shopee | [Backend Engineer Intern, Data Infrastructure - OLAP (Fall 2026/ Spring 2027)](<https://careers.shopee.sg/job-detail/J02191248/1>) | OLAP/big-data engine development; Fall 2026 and Spring 2027. |
| 28 | OCBC | [Internship: Group Risk Management, Group Risk Portfolio Management, Provision & Capital Analytics [Jan to May 2027]](<https://ocbc.wd102.myworkdayjobs.com/External/job/OCBC-Singapore/Internship--Group-Risk-Management--Group-Risk-Portfolio-Management--Provision---Capital-Analytics--Jan-to-May-2027-_JR00010979-1>) | Dashboards, prototypes, automation and risk analytics; Jan–May 2027. |
| 29 | Sea | [Security Engineering Intern](<https://career.sea.com/position/J02180598>) | Security research, testing, technical investigation and tooling. |
| 30 | Grab | [Intern, Strategy & Analytics, Transport](<https://jobs.smartrecruiters.com/Grab/744000149793152>) | Business analytics and A/B testing; retained under the documented analytics scope. |

## Recovered listings

- TikTok: [Governance Track LLM Product Intern（TikTok Platform Safety）- 2027 Start](<https://lifeattiktok.com/search/7669738564847110453>)
- Shopee: [Business Intelligence Intern (Spring 2027)](<https://careers.shopee.sg/job-detail/J02185576/1>)
- Shopee: [Business Intelligence Intern (Spring 2027)](<https://careers.shopee.sg/job-detail/J00003615/1>)
- Shopee: [Regional Large Language Model (LLM) Agent & Prompt Engineering Intern (Spring 2027)](<https://careers.shopee.sg/job-detail/J02042064/1>)
- Shopee: [Business Intelligence (BI) Intern – Cross Border E-commerce (Summer 2026)](<https://careers.shopee.sg/job-detail/J00356170/1>)
- Shopee: [Product Manager Intern, Traffic & Content - LLM Feature (Fall 2026)](<https://careers.shopee.sg/job-detail/J02102662/1>)
- Micron: [Intern- Silicon Design Validation Engineer](<https://micron.wd1.myworkdayjobs.com/External/job/MSB-Singapore/Intern--Silicon-Design-Validation-Engineer_JR111158>)

The two additional LLM product roles were reviewed after the full collection completed: Shopee includes prompt orchestration, model evaluation and technical product requirements; TikTok includes risk analysis, data tracking and security monitoring. Both fit the documented technology product/analytics scope.

All 20 sources completed successfully at 2026-09-24T09:16:34.175346+00:00. The refreshed snapshot contains 412 active listings. All 71 tests pass. A separate in-memory simulation of all 405 pre-audit active records confirmed survival after one complete absence, closure after two, and outage resets; it did not modify published history.
