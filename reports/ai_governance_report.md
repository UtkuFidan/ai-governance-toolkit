# AI governance report

As of 2026-10-28. Illustrative example data only. Entries are generic descriptions modelled on public portfolio projects and common industry use cases. Not a real register, not legal advice.

> Screening aid, not legal advice. Classification depends on facts and on the final legal reading of Regulation (EU) 2024/1689 and later amendments or guidelines; have counsel confirm any tier that matters.

## 1. Summary

- Systems in register: 12 (11 in production or pilot)
- Tiers: prohibited 1, high-risk 3, limited-risk (transparency) 2, minimal 6
- Systems using personal data: 10
- Control gaps found by register checks: 26 across 8 systems
- Live systems without validation in the last 12 months: 4 (AI-002, AI-004, AI-009, AI-010)

## 2. Register

| ID | System | Owner | Status | Model | Deployment | Oversight | Personal data | Last validation | Incidents |
|---|---|---|---|---|---|---|---|---|---|
| AI-001 | Explainable card-fraud scoring (gradient-boosted trees) | Head of Fraud Analytics | production | XGBoost classifier with TreeSHAP reason codes | on_prem | human_in_the_loop | yes | 2026-03-12 | 0 |
| AI-002 | Retail credit scorecard | Head of Retail Credit Risk | production | Logistic regression scorecard with WoE binning | on_prem | human_on_the_loop | yes | 2025-06-30 | 1 |
| AI-003 | Transaction-monitoring alert prioritisation | Head of Financial Crime Analytics | production | Gradient-boosted trees on top of rule-based scenarios | on_prem | human_in_the_loop | yes | 2026-01-20 | 0 |
| AI-004 | Sanctions name-screening match ranker | Head of Sanctions Compliance | production | Fuzzy string matching with a learned re-ranker | on_prem | human_in_the_loop | yes | 2025-09-15 | 0 |
| AI-005 | Local-LLM RAG assistant for regulations | Head of Audit Analytics | pilot | Open-weight LLM with retrieval-augmented generation | local_workstation | human_in_the_loop | no | 2026-08-05 | 1 |
| AI-006 | Customer churn and uplift model | Head of Customer Analytics | production | Gradient-boosted churn model plus uplift (two-model approach) | private_cloud | none | yes | 2025-12-02 | 0 |
| AI-007 | Energy consumption forecasting | Head of Facilities Analytics | production | Gradient-boosted regression with calendar and weather features | private_cloud | human_on_the_loop | no | 2026-04-28 | 0 |
| AI-008 | Motor insurance pricing and claims frequency model | Head of Pricing | production | Generalised linear model with gradient-boosted challenger | on_prem | human_on_the_loop | yes | 2026-05-10 | 0 |
| AI-009 | Life and health insurance risk-pricing model (pilot) | Head of Life Underwriting | pilot | Survival model with gradient-boosted features | private_cloud | post_hoc_sampling | yes | none | 0 |
| AI-010 | Vendor CV-screening tool | Head of HR Operations | production | Vendor-supplied ranking model (opaque) | vendor_saas | none | yes | 2024-11-10 | 1 |
| AI-011 | Vendor customer-service chatbot | Head of Customer Service | production | Vendor-hosted large language model with a knowledge base | vendor_saas | human_on_the_loop | yes | 2026-02-18 | 0 |
| AI-012 | Customer social-behaviour scoring (rejected proposal) | Head of Retail Marketing | rejected | Behavioural scoring model (concept only) | private_cloud | none | yes | none | 0 |

## 3. EU AI Act risk tiers

| ID | Tier | References | Rationale |
|---|---|---|---|
| AI-001 | minimal | Annex III 5(b) fraud carve-out | No Art 5 practice, Art 6 high-risk route or Art 50 transparency trigger was indicated by the answers. Annex III 5(b) excludes AI systems used for the purpose of detecting financial fraud; this route to high-risk does not apply. Art 4 (AI literacy) applies to providers and deployers of AI systems generally. |
| AI-002 | high-risk | Annex III 5(b), Art 6(2) | Annex III point 5(b): Creditworthiness of natural persons or credit scoring (fraud detection excepted). |
| AI-003 | minimal | none | No Art 5 practice, Art 6 high-risk route or Art 50 transparency trigger was indicated by the answers. Art 4 (AI literacy) applies to providers and deployers of AI systems generally. |
| AI-004 | minimal | none | No Art 5 practice, Art 6 high-risk route or Art 50 transparency trigger was indicated by the answers. Art 4 (AI literacy) applies to providers and deployers of AI systems generally. |
| AI-005 | limited-risk (transparency) | Art 50 | Transparency duty indicated: system interacts directly with natural persons (Art 50(1)). Transparency duty indicated: system generates synthetic audio, image, video or text (Art 50(2)). Art 50(1) has an exception where the AI interaction is obvious to a reasonably well-informed person; check context. No personal-data category recorded. |
| AI-006 | minimal | none | No Art 5 practice, Art 6 high-risk route or Art 50 transparency trigger was indicated by the answers. Art 4 (AI literacy) applies to providers and deployers of AI systems generally. |
| AI-007 | minimal | none | No Art 5 practice, Art 6 high-risk route or Art 50 transparency trigger was indicated by the answers. Art 4 (AI literacy) applies to providers and deployers of AI systems generally. No personal-data category recorded. |
| AI-008 | minimal | none | No Art 5 practice, Art 6 high-risk route or Art 50 transparency trigger was indicated by the answers. Art 4 (AI literacy) applies to providers and deployers of AI systems generally. |
| AI-009 | high-risk | Annex III 5(c), Art 6(2) | Annex III point 5(c): Risk assessment and pricing for natural persons in life and health insurance. |
| AI-010 | high-risk | Annex III 4(a), Art 6(2) | Annex III point 4(a): Employment: recruitment or selection. |
| AI-011 | limited-risk (transparency) | Art 50 | Transparency duty indicated: system interacts directly with natural persons (Art 50(1)). Transparency duty indicated: system generates synthetic audio, image, video or text (Art 50(2)). Art 50(1) has an exception where the AI interaction is obvious to a reasonably well-informed person; check context. |
| AI-012 | prohibited | Art 5(1)(c) | Answers indicate social scoring leading to detrimental treatment (Art 5(1)(c)). |

Obligation articles to read for each tier (pointers only; read the Regulation for content):

- AI-002 (high-risk): Art 8; Art 9: Risk management system; Art 10: Data and data governance; Art 11: Technical documentation; Art 12: Record-keeping; Art 13: Transparency and provision of information to deployers; Art 14: Human oversight; Art 15: Accuracy, robustness and cybersecurity; Art 16: Obligations of providers of high-risk AI systems; Art 17: Quality management system; Art 26: Obligations of deployers of high-risk AI systems; Art 27: Fundamental rights impact assessment for high-risk AI systems; Art 43: Conformity assessment; Art 49: Registration; Art 72: Post-market monitoring by providers and post-market monitoring plan; Art 73: Reporting of serious incidents; Art 86: Right to explanation of individual decision-making
- AI-005 (limited-risk (transparency)): Art 50: Transparency obligations for providers and deployers of certain AI systems
- AI-009 (high-risk): Art 8; Art 9: Risk management system; Art 10: Data and data governance; Art 11: Technical documentation; Art 12: Record-keeping; Art 13: Transparency and provision of information to deployers; Art 14: Human oversight; Art 15: Accuracy, robustness and cybersecurity; Art 16: Obligations of providers of high-risk AI systems; Art 17: Quality management system; Art 26: Obligations of deployers of high-risk AI systems; Art 27: Fundamental rights impact assessment for high-risk AI systems; Art 43: Conformity assessment; Art 49: Registration; Art 72: Post-market monitoring by providers and post-market monitoring plan; Art 73: Reporting of serious incidents; Art 86: Right to explanation of individual decision-making
- AI-010 (high-risk): Art 26: Obligations of deployers of high-risk AI systems; Art 86: Right to explanation of individual decision-making
- AI-011 (limited-risk (transparency)): Art 50: Transparency obligations for providers and deployers of certain AI systems
- AI-012 (prohibited): Art 5: Prohibited AI practices

### Application dates as of 2026-10-28

Dates are from Art 113 of Regulation (EU) 2024/1689 as amended by Regulation (EU) 2026/1744 (in force 27 July 2026). A date shown with an earlier original date has been postponed by that amendment.

| Obligation group | Applies from | Original date | Applies on the report date |
|---|---|---|---|
| Prohibited AI practices | 2025-02-02 | 2025-02-02 | yes |
| AI literacy | 2025-02-02 | 2025-02-02 | yes |
| Governance bodies, notified bodies, penalties (Chapters III s.4, VII, XII; Art 78) | 2025-08-02 | 2025-08-02 | yes |
| General-purpose AI model obligations (Chapter V) | 2025-08-02 | 2025-08-02 | yes |
| Transparency obligations (Art 50) | 2026-08-02 | 2026-08-02 | yes |
| Art 50(2) machine-readable marking, generative systems already on the market before 2 August 2026 | 2026-12-02 | 2026-08-02 | no |
| Added prohibitions (non-consensual intimate imagery, child sexual abuse material) | 2026-12-02 | new | no |
| High-risk systems under Annex III (Art 6(2)) and their requirements | 2027-12-02 | 2026-08-02 | no |
| High-risk systems that are products or safety components under Annex I (Art 6(1)) | 2028-08-02 | 2027-08-02 | no |

| ID | Tier | Obligation groups that follow from the tier | Already applicable | Not yet applicable |
|---|---|---|---|---|
| AI-001 | minimal | 1 | ai_literacy | none |
| AI-002 | high-risk | 2 | ai_literacy | high_risk_annex_iii (2027-12-02) |
| AI-003 | minimal | 1 | ai_literacy | none |
| AI-004 | minimal | 1 | ai_literacy | none |
| AI-005 | limited-risk (transparency) | 2 | ai_literacy, transparency | none |
| AI-006 | minimal | 1 | ai_literacy | none |
| AI-007 | minimal | 1 | ai_literacy | none |
| AI-008 | minimal | 1 | ai_literacy | none |
| AI-009 | high-risk | 2 | ai_literacy | high_risk_annex_iii (2027-12-02) |
| AI-010 | high-risk | 2 | ai_literacy | high_risk_annex_iii (2027-12-02) |
| AI-011 | limited-risk (transparency) | 2 | ai_literacy, transparency | none |
| AI-012 | prohibited | 2 | ai_literacy, prohibitions | none |

## 4. Control gap assessment

`met` = the register entry is consistent with the control. `gap` = a register check failed. `evidence requested` = no automatic check; a document must be supplied. `met` does not prove the control works.

| ID | Tier | Controls applicable | Met | Gap | Evidence requested | Gaps |
|---|---|---|---|---|---|---|
| AI-001 | minimal | 9 | 7 | 0 | 2 | none |
| AI-002 | high-risk | 20 | 7 | 2 | 11 | DAT-01, VAL-01 |
| AI-003 | minimal | 9 | 6 | 1 | 2 | DAT-01 |
| AI-004 | minimal | 9 | 3 | 4 | 2 | DAT-01, DOC-01, VAL-01, MON-01 |
| AI-005 | limited-risk (transparency) | 10 | 7 | 1 | 2 | DAT-01 |
| AI-006 | minimal | 9 | 4 | 3 | 2 | DAT-01, DOC-01, MON-01 |
| AI-007 | minimal | 8 | 7 | 0 | 1 | none |
| AI-008 | minimal | 9 | 7 | 0 | 2 | none |
| AI-009 | high-risk | 20 | 3 | 6 | 11 | DAT-01, DOC-01, HUM-01, VAL-01, VAL-02, MON-01 |
| AI-010 | high-risk | 21 | 2 | 8 | 11 | DAT-01, DOC-01, HUM-01, VAL-01, VAL-02, MON-01, INC-01, THP-01 |
| AI-011 | limited-risk (transparency) | 12 | 8 | 1 | 3 | DAT-01 |
| AI-012 | prohibited | 1 | 1 | 0 | 0 | none |

### Gap detail

AI-002 Retail credit scorecard

- DAT-01 Data governance and documentation: no data dictionary listed
- VAL-01 Validation before use and periodically: last validation 2025-06-30 (485 days before 2026-10-28)

AI-003 Transaction-monitoring alert prioritisation

- DAT-01 Data governance and documentation: no data dictionary listed

AI-004 Sanctions name-screening match ranker

- DAT-01 Data governance and documentation: no data dictionary listed
- DOC-01 Technical documentation and model card: 1 document(s) listed (expect at least 2)
- VAL-01 Validation before use and periodically: last validation 2025-09-15 (408 days before 2026-10-28)
- MON-01 Performance monitoring with thresholds: frequency quarterly, 2 metric(s); thresholds defined: False

AI-005 Local-LLM RAG assistant for regulations

- DAT-01 Data governance and documentation: no data dictionary listed

AI-006 Customer churn and uplift model

- DAT-01 Data governance and documentation: no data dictionary listed
- DOC-01 Technical documentation and model card: 1 document(s) listed (expect at least 2)
- MON-01 Performance monitoring with thresholds: frequency quarterly, 2 metric(s); thresholds defined: False

AI-009 Life and health insurance risk-pricing model (pilot)

- DAT-01 Data governance and documentation: no data dictionary listed
- DOC-01 Technical documentation and model card: 0 document(s) listed (expect at least 2)
- HUM-01 Effective human oversight: oversight mode: post_hoc_sampling; reviewer can override: False
- VAL-01 Validation before use and periodically: no validation date recorded
- VAL-02 Independent validation: independent validation: False
- MON-01 Performance monitoring with thresholds: frequency none, 0 metric(s); thresholds defined: False

AI-010 Vendor CV-screening tool

- DAT-01 Data governance and documentation: no data dictionary listed
- DOC-01 Technical documentation and model card: 1 document(s) listed (expect at least 2)
- HUM-01 Effective human oversight: oversight mode: none; reviewer can override: False
- VAL-01 Validation before use and periodically: last validation 2024-11-10 (717 days before 2026-10-28)
- VAL-02 Independent validation: independent validation: False
- MON-01 Performance monitoring with thresholds: frequency none, 0 metric(s); thresholds defined: False
- INC-01 Incident handling and escalation: 1 open of 1 incident(s)
- THP-01 Third-party and vendor oversight: 0 non-marketing document(s) from or about the vendor

AI-011 Vendor customer-service chatbot

- DAT-01 Data governance and documentation: no data dictionary listed

### Evidence checklist per system

<details><summary>AI-001 Explainable card-fraud scoring (gradient-boosted trees) (2 open)</summary>

- [ ] GOV-02 AI literacy and competence (evidence requested): Training records or role competence matrix for owners; reviewers and users
- [ ] DAT-02 Personal-data minimisation and protection (evidence requested): Record of processing entry; privacy review. Data-protection law (e.g. GDPR) is out of scope for this tool

</details>

<details><summary>AI-002 Retail credit scorecard (13 open)</summary>

- [ ] GOV-02 AI literacy and competence (evidence requested): Training records or role competence matrix for owners; reviewers and users
- [ ] RSK-01 Risk management across the lifecycle (evidence requested): Risk register extract for the system; treatment decisions; last review date
- [ ] RSK-02 Impact assessment on affected people (evidence requested): Impact assessment; sign-off; mitigation list. Art 27(1) names Annex III points 5(b) and 5(c) for deployers
- [ ] DAT-01 Data governance and documentation (gap): Data dictionary; lineage note; data quality test results (see `ai-gov evidence`)
- [ ] DAT-02 Personal-data minimisation and protection (evidence requested): Record of processing entry; privacy review. Data-protection law (e.g. GDPR) is out of scope for this tool
- [ ] LOG-01 Event logging and traceability (evidence requested): Log schema; retention rule; sample of a reconstructed decision
- [ ] TRN-01 Instructions and information for deployers and users (evidence requested): Instructions for use; user guidance; known limitations statement
- [ ] VAL-01 Validation before use and periodically (gap): Validation report with date; scope; results and open findings
- [ ] FAI-01 Bias and fairness testing (evidence requested): Group metrics (demographic parity; equal opportunity) and a decision on tolerances (see `ai-gov evidence`)
- [ ] XAI-01 Explainability of outputs (evidence requested): Global drivers; per-case reason codes; reviewer feedback (see `ai-gov evidence`)
- [ ] SEC-01 Accuracy, robustness and security (evidence requested): Robustness tests; access control review; model artefact integrity checks
- [ ] CHG-01 Change and version control (evidence requested): Change log; approval records; model registry entry
- [ ] AUD-01 Internal audit and management review (evidence requested): Audit plan covering the system; last management review minutes

</details>

<details><summary>AI-003 Transaction-monitoring alert prioritisation (3 open)</summary>

- [ ] GOV-02 AI literacy and competence (evidence requested): Training records or role competence matrix for owners; reviewers and users
- [ ] DAT-01 Data governance and documentation (gap): Data dictionary; lineage note; data quality test results (see `ai-gov evidence`)
- [ ] DAT-02 Personal-data minimisation and protection (evidence requested): Record of processing entry; privacy review. Data-protection law (e.g. GDPR) is out of scope for this tool

</details>

<details><summary>AI-004 Sanctions name-screening match ranker (6 open)</summary>

- [ ] GOV-02 AI literacy and competence (evidence requested): Training records or role competence matrix for owners; reviewers and users
- [ ] DAT-01 Data governance and documentation (gap): Data dictionary; lineage note; data quality test results (see `ai-gov evidence`)
- [ ] DAT-02 Personal-data minimisation and protection (evidence requested): Record of processing entry; privacy review. Data-protection law (e.g. GDPR) is out of scope for this tool
- [ ] DOC-01 Technical documentation and model card (gap): Model card or development document; validation report
- [ ] VAL-01 Validation before use and periodically (gap): Validation report with date; scope; results and open findings
- [ ] MON-01 Performance monitoring with thresholds (gap): Monitoring dashboard export; threshold table; last two monitoring reports (see `ai-gov evidence`)

</details>

<details><summary>AI-005 Local-LLM RAG assistant for regulations (3 open)</summary>

- [ ] GOV-02 AI literacy and competence (evidence requested): Training records or role competence matrix for owners; reviewers and users
- [ ] DAT-01 Data governance and documentation (gap): Data dictionary; lineage note; data quality test results (see `ai-gov evidence`)
- [ ] TRN-02 Disclosure of AI interaction and generated content (evidence requested): Screenshots of the disclosure; marking or labelling approach for generated content

</details>

<details><summary>AI-006 Customer churn and uplift model (5 open)</summary>

- [ ] GOV-02 AI literacy and competence (evidence requested): Training records or role competence matrix for owners; reviewers and users
- [ ] DAT-01 Data governance and documentation (gap): Data dictionary; lineage note; data quality test results (see `ai-gov evidence`)
- [ ] DAT-02 Personal-data minimisation and protection (evidence requested): Record of processing entry; privacy review. Data-protection law (e.g. GDPR) is out of scope for this tool
- [ ] DOC-01 Technical documentation and model card (gap): Model card or development document; validation report
- [ ] MON-01 Performance monitoring with thresholds (gap): Monitoring dashboard export; threshold table; last two monitoring reports (see `ai-gov evidence`)

</details>

<details><summary>AI-007 Energy consumption forecasting (1 open)</summary>

- [ ] GOV-02 AI literacy and competence (evidence requested): Training records or role competence matrix for owners; reviewers and users

</details>

<details><summary>AI-008 Motor insurance pricing and claims frequency model (2 open)</summary>

- [ ] GOV-02 AI literacy and competence (evidence requested): Training records or role competence matrix for owners; reviewers and users
- [ ] DAT-02 Personal-data minimisation and protection (evidence requested): Record of processing entry; privacy review. Data-protection law (e.g. GDPR) is out of scope for this tool

</details>

<details><summary>AI-009 Life and health insurance risk-pricing model (pilot) (17 open)</summary>

- [ ] GOV-02 AI literacy and competence (evidence requested): Training records or role competence matrix for owners; reviewers and users
- [ ] RSK-01 Risk management across the lifecycle (evidence requested): Risk register extract for the system; treatment decisions; last review date
- [ ] RSK-02 Impact assessment on affected people (evidence requested): Impact assessment; sign-off; mitigation list. Art 27(1) names Annex III points 5(b) and 5(c) for deployers
- [ ] DAT-01 Data governance and documentation (gap): Data dictionary; lineage note; data quality test results (see `ai-gov evidence`)
- [ ] DAT-02 Personal-data minimisation and protection (evidence requested): Record of processing entry; privacy review. Data-protection law (e.g. GDPR) is out of scope for this tool
- [ ] DOC-01 Technical documentation and model card (gap): Model card or development document; validation report
- [ ] LOG-01 Event logging and traceability (evidence requested): Log schema; retention rule; sample of a reconstructed decision
- [ ] TRN-01 Instructions and information for deployers and users (evidence requested): Instructions for use; user guidance; known limitations statement
- [ ] HUM-01 Effective human oversight (gap): Oversight procedure; reviewer training; override statistics
- [ ] VAL-01 Validation before use and periodically (gap): Validation report with date; scope; results and open findings
- [ ] VAL-02 Independent validation (gap): Validator independence statement; validation report
- [ ] FAI-01 Bias and fairness testing (evidence requested): Group metrics (demographic parity; equal opportunity) and a decision on tolerances (see `ai-gov evidence`)
- [ ] XAI-01 Explainability of outputs (evidence requested): Global drivers; per-case reason codes; reviewer feedback (see `ai-gov evidence`)
- [ ] SEC-01 Accuracy, robustness and security (evidence requested): Robustness tests; access control review; model artefact integrity checks
- [ ] MON-01 Performance monitoring with thresholds (gap): Monitoring dashboard export; threshold table; last two monitoring reports (see `ai-gov evidence`)
- [ ] CHG-01 Change and version control (evidence requested): Change log; approval records; model registry entry
- [ ] AUD-01 Internal audit and management review (evidence requested): Audit plan covering the system; last management review minutes

</details>

<details><summary>AI-010 Vendor CV-screening tool (19 open)</summary>

- [ ] GOV-02 AI literacy and competence (evidence requested): Training records or role competence matrix for owners; reviewers and users
- [ ] RSK-01 Risk management across the lifecycle (evidence requested): Risk register extract for the system; treatment decisions; last review date
- [ ] RSK-02 Impact assessment on affected people (evidence requested): Impact assessment; sign-off; mitigation list. Art 27(1) names Annex III points 5(b) and 5(c) for deployers
- [ ] DAT-01 Data governance and documentation (gap): Data dictionary; lineage note; data quality test results (see `ai-gov evidence`)
- [ ] DAT-02 Personal-data minimisation and protection (evidence requested): Record of processing entry; privacy review. Data-protection law (e.g. GDPR) is out of scope for this tool
- [ ] DOC-01 Technical documentation and model card (gap): Model card or development document; validation report
- [ ] LOG-01 Event logging and traceability (evidence requested): Log schema; retention rule; sample of a reconstructed decision
- [ ] TRN-01 Instructions and information for deployers and users (evidence requested): Instructions for use; user guidance; known limitations statement
- [ ] HUM-01 Effective human oversight (gap): Oversight procedure; reviewer training; override statistics
- [ ] VAL-01 Validation before use and periodically (gap): Validation report with date; scope; results and open findings
- [ ] VAL-02 Independent validation (gap): Validator independence statement; validation report
- [ ] FAI-01 Bias and fairness testing (evidence requested): Group metrics (demographic parity; equal opportunity) and a decision on tolerances (see `ai-gov evidence`)
- [ ] XAI-01 Explainability of outputs (evidence requested): Global drivers; per-case reason codes; reviewer feedback (see `ai-gov evidence`)
- [ ] SEC-01 Accuracy, robustness and security (evidence requested): Robustness tests; access control review; model artefact integrity checks
- [ ] MON-01 Performance monitoring with thresholds (gap): Monitoring dashboard export; threshold table; last two monitoring reports (see `ai-gov evidence`)
- [ ] INC-01 Incident handling and escalation (gap): Incident log; escalation procedure. Art 73 serious-incident reporting concerns providers of high-risk systems
- [ ] THP-01 Third-party and vendor oversight (gap): Due-diligence file; contract clauses on documentation and incident notice; vendor validation evidence
- [ ] CHG-01 Change and version control (evidence requested): Change log; approval records; model registry entry
- [ ] AUD-01 Internal audit and management review (evidence requested): Audit plan covering the system; last management review minutes

</details>

<details><summary>AI-011 Vendor customer-service chatbot (4 open)</summary>

- [ ] GOV-02 AI literacy and competence (evidence requested): Training records or role competence matrix for owners; reviewers and users
- [ ] DAT-01 Data governance and documentation (gap): Data dictionary; lineage note; data quality test results (see `ai-gov evidence`)
- [ ] DAT-02 Personal-data minimisation and protection (evidence requested): Record of processing entry; privacy review. Data-protection law (e.g. GDPR) is out of scope for this tool
- [ ] TRN-02 Disclosure of AI interaction and generated content (evidence requested): Screenshots of the disclosure; marking or labelling approach for generated content

</details>

<details><summary>AI-012 Customer social-behaviour scoring (rejected proposal) (0 open)</summary>


</details>

### Control library coverage

| Control | Title | EU AI Act | ISO/IEC 42001 theme | NIST AI RMF |
|---|---|---|---|---|
| PRH-01 | Screen for prohibited practices | Art 5 | Planning: risk and impact identification; Operation: operational planning and control | MAP 1 |
| GOV-01 | Accountable owner and AI policy | Art 17 | Leadership: policy and roles; Annex A topic: policies; internal organisation | GOVERN 1, GOVERN 2 |
| GOV-02 | AI literacy and competence | Art 4 | Support: competence and awareness | GOVERN 2 |
| RSK-01 | Risk management across the lifecycle | Art 9 | Planning: risk assessment and treatment; Operation: risk assessment and treatment | MAP 5, MANAGE 1 |
| RSK-02 | Impact assessment on affected people | Art 27 | Planning and operation: AI system impact assessment; Annex A topic: assessing impacts | MAP 5 |
| DAT-01 | Data governance and documentation | Art 10 | Annex A topic: data for AI systems | MAP 4, MEASURE 2 |
| DAT-02 | Personal-data minimisation and protection | - | Annex A topic: data for AI systems; Operation: impact assessment | MEASURE 2 |
| DOC-01 | Technical documentation and model card | Art 11 | Support: documented information; Annex A topic: AI system life cycle | MAP 2, GOVERN 1 |
| LOG-01 | Event logging and traceability | Art 12 | Annex A topic: AI system life cycle; Operation: operational control | MEASURE 3 |
| TRN-01 | Instructions and information for deployers and users | Art 13 | Annex A topic: information for interested parties | GOVERN 5, MAP 3 |
| TRN-02 | Disclosure of AI interaction and generated content | Art 50 | Annex A topic: information for interested parties | GOVERN 5, MAP 3 |
| HUM-01 | Effective human oversight | Art 14, Art 26 | Annex A topic: use of AI systems; Operation: operational control | GOVERN 3, MANAGE 1 |
| VAL-01 | Validation before use and periodically | Art 9, Art 15, Art 17 | Operation: verification and validation; Performance evaluation: monitoring and measurement | MEASURE 1, MEASURE 2 |
| VAL-02 | Independent validation | - | Performance evaluation: internal audit | MEASURE 1 |
| FAI-01 | Bias and fairness testing | Art 10 | Annex A topic: assessing impacts; Annex A topic: data for AI systems | MEASURE 2, MAP 5 |
| XAI-01 | Explainability of outputs | Art 13, Art 86 | Annex A topic: information for interested parties | MEASURE 2 |
| SEC-01 | Accuracy, robustness and security | Art 15 | Annex A topic: AI system life cycle; Operation: operational control | MEASURE 2, MANAGE 2 |
| MON-01 | Performance monitoring with thresholds | Art 72 | Performance evaluation: monitoring and measurement | MEASURE 3, MANAGE 4 |
| INC-01 | Incident handling and escalation | Art 73 | Improvement: nonconformity and corrective action | MANAGE 4 |
| THP-01 | Third-party and vendor oversight | Art 13, Art 26 | Annex A topic: third-party and customer relationships | GOVERN 6, MANAGE 3 |
| CHG-01 | Change and version control | Art 17 | Operation: operational planning and control; Annex A topic: AI system life cycle | MANAGE 1 |
| AUD-01 | Internal audit and management review | - | Performance evaluation: internal audit; management review | GOVERN 1 |

NIST AI RMF function coverage: GOVERN 8 controls; MAP 8 controls; MEASURE 9 controls; MANAGE 7 controls

## 5. Technical evidence

Dataset: UCI Default of Credit Card Clients (UCI 350), CC BY 4.0, Yeh (2009), DOI 10.24432/C55S3H. Seed 42. Illustrative model, not one of the register systems.

Model: HistGradientBoostingClassifier (scikit-learn), SEX excluded from features. Train/validation/test 18000/6000/6000; test AUC 0.7859 (95% bootstrap interval 0.7713 to 0.7996); default rate 0.2212; decision threshold 0.27 (max F1 on validation); flag rate on test 0.2393.

| Check | Status | Key metrics |
|---|---|---|
| drift_psi: test vs train (random split baseline) | pass | score_psi 0.0017, max_feature_psi 0.0034, features_over_0.10 0, features_over_0.25 0 |
| drift_psi: simulated shift: customers aged 40+ vs train | warn | score_psi 0.0081, max_feature_psi 5.658, features_over_0.10 2, features_over_0.25 2 |
| fairness: SEX | pass | demographic_parity_difference 0.0323, equal_opportunity_difference 0.0343, disparate_impact_ratio 0.8753 |
| fairness: AGE group (proxy) | pass | demographic_parity_difference 0.0404, equal_opportunity_difference 0.0162, disparate_impact_ratio 0.8489 |
| fairness: intersectional SEX x AGE | warn | cells_total 8, cells_included 8, min_cell_size 100, demographic_parity_difference 0.1242, equal_opportunity_difference 0.1302, disparate_impact_ratio 0.5944, highest_selection_cell female|50+, lowest_selection_cell female|30-39 |
| explainability_coverage | pass | features_total 22, features_for_80pct_importance 8, documented_importance_share 1.0, reason_code_share 0.981 |
| data_documentation_completeness | warn | columns 25, column_coverage 1.0, field_completeness 1.0, columns_with_domain_check 18, columns_with_values_outside_domain 8, domain_conformity 0.7764, missing_value_share 0.0, duplicate_rows 0, target_documented True |

- fairness: SEX: selection rate {'female': 0.2266, 'male': 0.2589}, true-positive rate {'female': 0.5868, 'male': 0.5524}; 95% bootstrap interval: demographic parity difference [0.0099, 0.0524], equal opportunity difference [0.0018, 0.0867], disparate impact ratio [0.8056, 0.9595]
- fairness: AGE group (proxy): selection rate {'40+': 0.2671, 'under 40': 0.2268}, true-positive rate {'40+': 0.5824, 'under 40': 0.5663}; 95% bootstrap interval: demographic parity difference [0.0164, 0.0641], equal opportunity difference [0.0009, 0.0726], disparate impact ratio [0.7746, 0.9346]
- fairness: intersectional SEX x AGE: 8 of 8 cells have at least 100 people. Demographic parity difference 0.1242, equal opportunity difference 0.1302, disparate impact ratio 0.5944; highest selection rate in female|50+, lowest in female|30-39. 95% bootstrap interval: demographic parity difference [0.0842, 0.1817], equal opportunity difference [0.1013, 0.2766].

| Cell (sex, age band) | n | Selection rate (95% CI) | True-positive rate (95% CI) | Compared |
|---|---|---|---|---|
| female|30-39 | 1302 | 0.182 (0.162 to 0.2039) | 0.5108 (0.4467 to 0.5746) | yes |
| female|40-49 | 722 | 0.2493 (0.2191 to 0.2821) | 0.614 (0.5393 to 0.6837) | yes |
| female|50+ | 320 | 0.3063 (0.2583 to 0.3588) | 0.641 (0.5303 to 0.7385) | yes |
| female|<30 | 1284 | 0.2391 (0.2166 to 0.2632) | 0.6182 (0.5595 to 0.6736) | yes |
| male|30-39 | 904 | 0.2423 (0.2155 to 0.2712) | 0.5529 (0.485 to 0.6189) | yes |
| male|40-49 | 574 | 0.2648 (0.2304 to 0.3024) | 0.5374 (0.4569 to 0.616) | yes |
| male|50+ | 252 | 0.2738 (0.2225 to 0.332) | 0.5352 (0.4204 to 0.6464) | yes |
| male|<30 | 642 | 0.271 (0.2381 to 0.3067) | 0.5753 (0.4942 to 0.6526) | yes |

- Values outside the documented domain: EDUCATION [0, 5, 6] (1.1% of rows); MARRIAGE [0] (0.2% of rows); PAY_0 [-2, 0] (58.3% of rows); PAY_2 [-2, 0] (65.0% of rows); PAY_3 [-2, 0] (66.2% of rows); PAY_4 [-2, 0] (69.3% of rows); PAY_5 [-2, 0] (71.6% of rows); PAY_6 [-2, 0] (70.6% of rows)

- drift_psi: test vs train (random split baseline): PSI < 0.10 stable, 0.10 to 0.25 moderate shift, >= 0.25 significant shift (common convention).
- drift_psi: simulated shift: customers aged 40+ vs train: PSI < 0.10 stable, 0.10 to 0.25 moderate shift, >= 0.25 significant shift (common convention).
- fairness: SEX: 'Positive' means predicted default (adverse). Differences are gaps in rates, not proof of discrimination; base rates differ between groups and the tolerance is illustrative. A point estimate inside the tolerance is reported as warn when its 95% bootstrap interval reaches beyond it.
- fairness: AGE group (proxy): 'Positive' means predicted default (adverse). Differences are gaps in rates, not proof of discrimination; base rates differ between groups and the tolerance is illustrative. A point estimate inside the tolerance is reported as warn when its 95% bootstrap interval reaches beyond it.
- fairness: intersectional SEX x AGE: Gaps are the maximum difference between cells, so they exceed single-attribute gaps by construction and with more cells the maximum drifts upward through noise alone. Read them together with the interval and the cell sizes.
- explainability_coverage: Importance is permutation-based (drop in AUC). Reason-code share uses single-feature occlusion to the training median; both are approximations to be confirmed with the model's own explanation method.
- data_documentation_completeness: Fails when columns lack a dictionary entry or required fields are blank; warns when data holds values the dictionary does not define.

## 6. Incident lessons

Failure-mode categories mapped to the controls that would be expected to catch them. Source for incident counts: [AI Incident Database](https://incidentdatabase.ai/) snapshots; the database's licence excludes report text, so this repo stores no incident text, only the author's category mapping. No incident counts are shown: the snapshot host (pub-72b2b2fc36ec423189843747af98f80e.r2.dev) timed out on repeated requests on 2026-10-28, the GraphQL API accepts only authorised origins, and the GitHub repository holds code without data.

| Category | Controls expected to catch it | Why |
|---|---|---|
| Discriminatory or unequal outcomes | DAT-01, FAI-01, RSK-02, VAL-01, MON-01 | Group-level testing before release and during monitoring surfaces unequal error or selection rates; the impact assessment asks who could be harmed. |
| Performance degradation or model drift | VAL-01, MON-01, CHG-01 | Thresholded monitoring (for example PSI on score and inputs) and periodic revalidation catch a model that no longer matches its population. |
| Fabricated or misleading generative output | VAL-01, HUM-01, TRN-02, MON-01, TRN-01 | Sampled accuracy tests, citation checks, a human who verifies before reliance, and clear disclosure of AI-generated content. |
| Privacy or data exposure | DAT-02, SEC-01, THP-01, PRH-01 | Data minimisation, access control and vendor due diligence reduce exposure; the prohibited-practice screen covers some biometric uses. |
| Automated decision without effective human oversight | HUM-01, RSK-01, LOG-01, RSK-02 | A defined override path, risk assessment of the decision, and logs that allow an affected person's case to be reconstructed. |
| Adversarial misuse or security failure | SEC-01, MON-01, INC-01, CHG-01 | Robustness testing, monitoring for abnormal inputs and an incident process that can respond. |
| Opaque third-party system | THP-01, TRN-01, XAI-01, VAL-02 | Contract rights to documentation and incident notice, plus independent validation of what cannot be inspected. |
| Physical safety or critical-service failure | RSK-01, SEC-01, HUM-01, LOG-01, INC-01 | Lifecycle risk management, fail-safe oversight and event logs that support investigation and reporting. |
| Slow or absent incident response | INC-01, LOG-01, AUD-01, GOV-01 | A tested escalation path, accountable owner and audit follow-up make sure known problems are closed. |

## 7. Sources and limits

- [Regulation (EU) 2024/1689 (AI Act), official text](https://eur-lex.europa.eu/eli/reg/2024/1689/oj): EU law, reuse permitted with attribution (Decision 2011/833/EU)
- [Regulation (EU) 2026/1744 (Digital Omnibus on AI), amended application dates](https://eur-lex.europa.eu/eli/reg/2026/1744/oj): EU law, reuse permitted with attribution; dates cross-checked on the AI Act Service Desk timeline
- [NIST AI Risk Management Framework 1.0 (NIST AI 100-1)](https://www.nist.gov/itl/ai-risk-management-framework): US government work, public domain
- [ISO/IEC 42001:2023](https://www.iso.org/standard/81230.html): Copyrighted; only paraphrased clause themes used
- [UCI Default of Credit Card Clients (Yeh, 2009)](https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients): CC BY 4.0
- [AI Incident Database](https://incidentdatabase.ai/research/snapshots/): Snapshot collections CC BY-SA; report text excluded. Only counts and links used

Limits: register checks read declared facts, not live systems; 'met' is not an opinion on effectiveness; the tier is a screening result; examples are invented.

By Utku Fidan · utkufidan.com
