# Framework Mapping

Mapped 1 November 2026 against the full text of each document, and re-scored on Draft 0.6 on 2 November 2026. A Full score means the text tells the reader to do the thing, and for NIST that it would produce any record NIST asks for. It does not mean it was tested.

**What we claim:** this playbook draws on these frameworks, scaled for small teams, with stated omissions. We do not claim alignment, compliance or certification. NIST and ASEAN describe themselves as voluntary. IMDA's text does not use the word, and none of the three is presented as law. Each needs to be read directly by anyone relying on it, and laws such as data protection rules apply separately.

Section numbers refer to `playbook.md`. These frameworks do not address the maintainability of agent-written code, so section 16 has no counterpart for that aim. Some of its controls do meet framework text: see the table below. They did not move any score on their own.

| Section 16 control | Framework text |
|---|---|
| Guard the tests, put architecture rules in tools, enforce the map in CI | IMDA 2.3.1 p33, building a procedure into the workflow |
| Feature map check on every change | IMDA 2.3.3 p45, change review; NIST MANAGE 4.1; ASEAN Guide p40, retest after tuning |
| See each proof fail | NIST MEASURE 2.13 |
| Keep the worker and the judge apart | NIST MEASURE 1.3 |
| Keep reading the code | IMDA 2.2.2 p30, domain expertise; IMDA 2.4.3 p47, tradecraft |

| Framework | Rows reviewed | Full | Partial | None | Not applicable |
|---|---|---|---|---|---|
| IMDA v1.5 | 160 | 62 | 73 | 25 | 0 |
| NIST AI 100-1 | 72 | 35 | 33 | 2 | 2 |
| ASEAN guides | 145 | 53 | 64 | 17 | 11 |

These are one strict reader's judgements, made by an AI model, not official scores, and they show spread only. Apart from NIST's 72 subcategories, the rows are our own breakdown. Scored on Draft 0.6 on 2 November 2026. A blind second scoring of 40 random rows matched 30, and marked 6 of the 18 sampled Full rows as Partial, so treat the Full counts as an upper estimate.

## IMDA Model AI Governance Framework For Agentic AI

Version 1.5, published 20 May 2026, updated 5 June 2026. This is the only one of the three written for agents. It describes itself as a living document, so check for a newer version.

| IMDA part | Playbook | Files | Full / Partial / None | Stated limits |
|---|---|---|---|---|
| Assess and bound the risks upfront | 1, 3, 4, 5 | `risk-card.md`, `approval-matrix.md` | 13 / 17 / 2 | Agent identity is basic, with no cryptographic identity |
| Make humans meaningfully accountable | 2, 4, 8, 12, 13 | `agent-inventory.md`, `approval-matrix.md` | 14 / 14 / 6 | Vendor contract terms are prompts, not legal drafting |
| Implement technical controls and processes | 5, 6, 7, 9, 11, 15, 16 | `pre-launch-checklist.md`, `incident-runbook.md` | 20 / 27 / 12 | Monitoring is sized for small teams, and no anomaly detection |
| Enable end-user responsibility | 9, 13 | `pre-launch-checklist.md` | 8 / 8 / 4 | Short coverage of disclosure, training and skills |
| Introduction and overview | 1, 2, 3 | | 7 / 7 / 1 | Multi-agent risks out of scope |

IMDA's four levels of human involvement, compared with this playbook:

| Playbook level | Nearest IMDA level |
|---|---|
| 0 Read | None. IMDA treats read-only as a limit on what the agent can do |
| 1 Draft | Agent proposes, human operates, loosely. A person acts on the draft |
| 2 Act with approval | Agent proposes, human operates, where every action is approved. Agent and human collaborate, where only significant steps are |
| 3 Act within limits | Agent operates, human observes. An agent mixing level 3 work with level 2 approvals on critical actions matches Agent operates, human approves |

**Not from IMDA, so do not attribute it there:** one-day adoption, a single part-time owner, drills, rollback plans as a named requirement, requester approval, the outcome counts in section 11, the 30, 60 and 90-day timing.

**Deliberately left out for this audience:** multi-agent systems, computer-use agents, customer-facing agents, cryptographic agent identity, agents monitoring agents, outlier approver analytics, observability platforms, formal threat modelling, MCP gateways, per-action runtime authorisation, user-set limits, task and system complexity as risk factors, a security role before an incident, model-based safeguards, strict tool input formats, handing credential entry to a person, standard transaction protocols, mixed evaluation methods, categorising changes by risk, central handling of model changes, attention to anthropomorphic design, telling users how their data is used, and teaching staff when and how to use agents, with refreshers.

## NIST AI Risk Management Framework

NIST AI 100-1, AI RMF 1.0, January 2023. NIST says it is being revised. NIST lets users select from its 72 subcategories, and notes that small to medium-sized organisations may face different challenges. As of this date we found no published NIST guideline for agents, only drafts and research.

The playbook addresses selected outcomes:

| Function | Playbook | Files | Stated limits |
|---|---|---|---|
| Govern | 1, 2, 3, 4, 6, 8, 9, 12, 13, 14, 15 | `risk-card.md`, `agent-inventory.md` | Workforce diversity outcomes are only touched: the people doing the work shape the rules, and nothing asks for other disciplines |
| Map | 1, 2, 3, 4, 5, 10, 12 | `risk-card.md` | Assumes third-party agents. No model-level assessment |
| Measure | 6, 7, 8, 9, 10, 11, 15, 16 | `pre-launch-checklist.md` | No fairness testing, explainability or environmental measures |
| Manage | 1, 5, 9, 10, 11, 12, 13, 14, 15 | `incident-runbook.md` | Risks are rated but not ranked. Models are rechecked on a change, with no routine watch between changes |

Prompt injection is not covered in AI 100-1. Section 4 draws on later work, listed in `evidence.md`.

## ASEAN Guide On AI Governance And Ethics

The 2024 Guide is written for organisations, and it is the primary source here. The Expanded Guide on Generative AI (2025) is mainly addressed to ASEAN policymakers. The 2024 Guide says it is voluntary, the Expanded Guide does not claim force of law, **neither gives guidance on agents**, and we found no ASEAN document on agentic AI, so this is an analogy.

| ASEAN component | Playbook | Stated limits |
|---|---|---|
| Internal governance structures and measures | 1, 2, 13, 15 | Light by design. The Guide itself notes a central body may be too heavy for small companies |
| Determining the level of human involvement | 1, 3, 4, 8, `risk-card.md` | Adapted from the Guide's probability and severity method |
| Operations management | 5, 6, 7, 9, 10, 11 | No data lineage or model work |
| Stakeholder interaction and communication | 13 | Covers disclosure, feedback and human review in short form |

| ASEAN level of involvement | Playbook |
|---|---|
| Human-in-the-loop | Levels 0, 1, and 2 by interpretation. The Guide's first sense has AI only recommending |
| Human-over-the-loop | Level 3 is the closest fit. Sampling plus a stop method is lighter than the Guide's supervising role |
| Human-out-of-the-loop | Deliberately excluded |

| ASEAN principle | Playbook | Coverage |
|---|---|---|
| Transparency and Explainability | 6, 13 | Partial: traceability and disclosure, no explainability |
| Fairness and Equity | None | **Not covered.** Agents that decide about people are out of scope |
| Security and Safety | 1, 4, 5, 9 | Partial |
| Human-centricity | 13 | Partial |
| Privacy and Data Governance | 5, 6, 12 | Partial |
| Accountability and Integrity | 2, 9, 13 | Partial, strongest area |
| Robustness and Reliability | 7, 11 | Partial |

## Other Useful References

These are open and free, and they fit parts of this playbook: Careful Adoption of Agentic AI Services (Five Eyes agencies, 2026), the strongest agent-specific government source, which is stricter on scope than this playbook; OWASP Top 10 for Agentic Applications 2026 and OWASP Top 10 for LLM Applications 2025, NIST SP 800-53 Rev. 5, NIST AI 600-1, and the AWS Agentic AI Security Scoping Matrix. EU AI Act Articles 12, 14 and 26 cover high-risk systems, from 2 December 2027 or 2 August 2028 under Regulation (EU) 2026/1744. Whether they will apply to you is a legal question. See `evidence.md`.

## Sources

- [IMDA v1.5](https://www.imda.gov.sg/-/media/imda/files/about/emerging-tech-and-research/artificial-intelligence/mgf-for-agentic-ai.pdf)
- [NIST AI 100-1](https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf)
- [NIST AI 600-1](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)
- [ASEAN Guide, 2024](https://asean.org/wp-content/uploads/2024/02/ASEAN-Guide-on-AI-Governance-and-Ethics_beautified_201223_v2.pdf)
- [Expanded ASEAN Guide on Generative AI, 2025](https://asean.org/wp-content/uploads/2025/01/Expanded-ASEAN-Guide-on-AI-Governance-and-Ethics-Generative-AI.pdf)
