# Evidence Behind The Defaults

Checked 1 November 2026, with the section 16 rows added 2 November 2026. This shows where each default comes from, so nobody mistakes a judgement call for a standard.

**The short answer:** there is no proven, validated standard for how much autonomy to give an AI agent. Least privilege and stop capability rest on established standards. Most of the rest is well-reasoned guidance, and some of it is this playbook's own judgement. We say which is which.

**Evidence types, strongest first for general use:** formal standard, binding law (narrow scope), government guidance, peer-reviewed study, community standard, vendor guidance, preprint, opinion. Guidance is voluntary unless marked as law.

| Default | Verdict | Best support | What is not established |
|---|---|---|---|
| Agents only for low-risk, non-sensitive tasks | **Not followed in full** | Careful Adoption pp4, 15, 25 (Five Eyes agencies, government guidance) | This playbook allows more, with approval and limits. That is our judgement |
| Least privilege | **Backed** | NIST SP 800-53 AC-6 (formal standard), Careful Adoption, OWASP LLM06:2025, NCSC UK | Nothing material |
| Stop capability and drills | **Backed** | NIST SP 800-53 IR-3 and IR-4 (formal standard), EU AI Act Art 14(4)(e) for high-risk systems, NIST AI 600-1 MG-2.4 | No body sets a drill frequency |
| Silence and unknown actions: deny | **Backed by guidance** | IMDA v1.5 §2.2.2, Careful Adoption p20 (stop and escalate when uncertain), OpenAI guardrails docs (for cybersecurity workflows only) | No formal standard says this for agents |
| Limits in the system, not only instructions | **Backed by guidance** | IMDA v1.5 §2.1.2 and §2.3.1, Careful Adoption, NCSC UK, Google, AWS | Which limits suit a small team is our judgement |
| Instructions in content are data | **Goal backed. Not a control** | NCSC UK, OWASP LLM01:2025 and ASI01, Google, NIST CAISI (over 250,000 attempts, at least one success against each of 13 frontier models) | NCSC says injection may never be fully mitigated, so the rule only reduces risk |
| Feature map | **Our method. One small pilot and one agent trial** | Traceability, plus Anthropic's code migration write-up (validate a judge against broken code) and verification loops article (check each change against a spec). The combination with a required check is ours | One repo, one replayed regression, one agent trial on a sample project. Not tested over time, or on a real pull request |
| Guard tests from weakening | **Practitioner guidance** | Horthy, Why Software Factories Fail, on commenting out a failing test or adding a mock. Anthropic's code migration write-up warns of weakened tests too | No controlled study found. How often this happens is unknown |
| Decide before code, thin slices, small reviews | **Practitioner guidance** | Horthy, from his own team's experience, and his [note on where the time goes](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/side-quests/where-does-the-time-go.md). He says his maintainability claims are not proven | The sizes and time savings are estimates, and he sells tools in this space |
| Keep the worker and the judge apart | **Vendor guidance** | Anthropic, Harness design for long-running apps, and its code migration write-up | No formal standard. Anthropic reports evaluators lean generous, and can be unnecessary overhead for work the model does reliably |
| Keep checks out of reach | **Benchmark practice** | SlopCodeBench held-out tests | No study of this in teams |
| Architecture rules in tools | **Judgement, with vendor example** | Anthropic's verification loops article on project-specific rules | No study |
| Keep reading the code | **Practitioner opinion, and vendors differ** | Horthy for it. Anthropic's migration write-up says to review results for that kind of job | Nothing established |
| Agents can degrade code over time | **Benchmark, narrow** | SlopCodeBench, including HumanLayer's small run: no model finished with zero defects, complexity rose for all, and duplication differed by model | Small sample and strict scoring, with no quality guardrails in HumanLayer's run. In the paper's abstract, quality guidance lowered starting levels but not degradation rates. The link between these metrics and maintainability is not established |
| Session check (three-factor) | **Vendor guidance** | Meta, Agents Rule of Two | Not a standard |
| Four levels | **Partly backed** | Similar ladders at AWS and IMDA v1.5 §1.1.3, NIST AI 100-1 asks teams to define oversight | No scheme has been validated. The number four is a choice |
| Levels per action, not per agent | **Partly backed** | AWS, Four security principles, Careful Adoption p22 (classify actions by impact, likelihood and reversibility) | No scheme has been validated |
| Levels 0 and 1 are not risk-free | **Backed by research** | Onnasch et al. (meta-analysis, not AI agents), Parasuraman and Manzey, ASEAN Guide p26 | The link to agents is our reading |
| The action rows | **Partly backed** | Axes match the MCP tool annotations, IMDA checkpoints (§2.2.2), OpenAI and Microsoft reversibility ratings | The rows themselves are original. The routine-development row is this playbook's judgement, and it sits under Draft |
| One action or one written class | **Partly backed** | NIST SP 800-53 CM-3, MCP Tools, one IMDA case study (Tencent) uses session-scoped approval | Limits on standing classes are our judgement |
| Show the real command | **Vendor and community guidance** | Microsoft AI Red Team, OWASP ASI09, MCP Tools | No formal standard |
| Second approver for hard-to-undo actions | **Partly backed** | NIST SP 800-53 AC-5 and AC-3(2). DORA supports review by someone other than the author, not a second approver for hard-to-undo actions | No study of requester approval for agent output |
| Test across varied tasks, and repeat runs | **Backed by guidance** | IMDA v1.5 §2.3.2 (policy compliance, tool calling, realistic environment, repeated runs across varied data), Careful Adoption p7 (agents may behave differently under evaluation) | How many runs is our judgement |
| Risk to level table | **Partly backed** | ASEAN Guide pp24-26 method | The table's cut-offs are ours |
| Checked outcomes before raising a level | **Maths backed. Use is our judgement** | Exact zero-failure bound, known as the rule of three in its 3/N form (Newman; Hanley and Lippman-Hand, record only), AWS on evidence-based promotion | No body has adopted this for agents. No published evidence supports any fixed waiting period, so we removed the four-week default |
| Approvals alone do not count as evidence | **Vendor data and guidance** | Anthropic's published 93% figure, IMDA v1.5 §2.2.2 | The figure is unaudited, and the post gives no method |
| Approval fatigue is real | **Backed by guidance and in neighbouring fields** | IMDA v1.5 §2.2.2 pp29-30 (alert fatigue and automation bias named; track override rate and response time; keep requests short with the risk clear). Anderson et al. on habituation. Goddard et al. and Parasuraman and Manzey on automation bias, a related effect. Akhawe and Felt show warning design changes behaviour, and that warnings can work | No peer-reviewed controlled study of agent permission prompts found |
| Audit log fields | **Partly backed** | NIST SP 800-53 AU-3, EU AI Act Art 12 for high-risk systems, IMDA v1.5 §2.3.3 | Retention is left to you unless law sets it |
| Tamper-resistant logs | **Backed by guidance** | NIST SP 800-53 AU-9, IMDA v1.5 §2.3.3 | Nothing material |
| Measure speed and stability together | **Survey-backed** | DORA 2025 | Correlation, not causation |
| Measure from systems, not impressions | **Experiment-backed** | METR randomised trial, early 2025 (preprint) | A small study of experienced developers on early-2025 tools. Later estimates are uncertain |
| Planted faults and written reasons for reviewers | **Written reasons: backed by guidance. Planted faults: partly backed** | IMDA v1.5 §2.2.2 p29 (written justification on high-risk approvals), Buçinca et al. on making people think first | No agent study, and no source for planted faults |
| Risk card | **Backed by guidance** | ASEAN Guide Annex A, NIST AI 100-1 GOVERN and MAP, IMDA v1.5 §2.1 | The format is ours |
| Retirement steps | **Backed by guidance** | NIST AI 100-1 GOVERN 1.7 and MANAGE 4.1, NIST AI 600-1 | Nothing material |
| Vendor questions | **Backed by guidance** | IMDA v1.5 §2.2.1, NIST AI 600-1 GV-6.1 and GV-6.2 | The list is ours |
| 30, 60 and 90-day rollout, one-day start | **Judgement only** | Gradual rollout is backed by IMDA v1.5 §2.3.3 | The timings are ours |

## Not Read

- ISO/IEC 42001, 42005 and 23894, and SAE J3016: paid standards, not read, and not relied on

## Sources

**Formal standards and law**

- [NIST SP 800-53 Rev. 5](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-53r5.pdf)
- [EU AI Act Art 12](https://artificialintelligenceact.eu/article/12/) and [Art 14](https://artificialintelligenceact.eu/article/14/), high-risk systems only, read on [EUR-Lex](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32024R1689)

**Government guidance**

- [IMDA Model AI Governance Framework for Agentic AI, v1.5](https://www.imda.gov.sg/-/media/imda/files/about/emerging-tech-and-research/artificial-intelligence/mgf-for-agentic-ai.pdf)
- [NIST AI RMF 1.0, AI 100-1](https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf) and [NIST AI 600-1](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)
- [ASEAN Guide on AI Governance and Ethics, 2024](https://asean.org/wp-content/uploads/2024/02/ASEAN-Guide-on-AI-Governance-and-Ethics_beautified_201223_v2.pdf)
- NCSC UK blogs: [Thinking carefully before adopting agentic AI](https://www.ncsc.gov.uk/blogs/thinking-carefully-before-adopting-agentic-ai), 15 May 2026, a summary of Careful Adoption, and [Prompt injection is not SQL injection](https://www.ncsc.gov.uk/blog-post/prompt-injection-is-not-sql-injection), 8 December 2025
- [Careful Adoption of Agentic AI Services](https://www.ncsc.govt.nz/assets/guidance/Documents/Careful-adoption-of-agentic-AI-services_FINAL.pdf), ASD's ACSC, CISA, NSA, Cyber Centre, NCSC-NZ and NCSC-UK, 1 May 2026, read from the NCSC-NZ copy
- [NIST CAISI, red-teaming competition insights](https://www.nist.gov/blogs/caisi-research-blog/insights-ai-agent-security-large-scale-red-teaming-competition)

**Community standards**

- [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/), [LLM01:2025](https://genai.owasp.org/llmrisk/llm01-prompt-injection/), [LLM06:2025](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/)
- [MCP Tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools) and [Schema](https://modelcontextprotocol.io/specification/2026-07-28/schema), revision of 28 July 2026. The tool annotations are unchanged from the 2025-11-25 revision

**Research**

- [METR randomised trial](https://arxiv.org/abs/2507.09089) and [2026 update](https://metr.org/blog/2026-02-24-uplift-update/)
- [DORA 2025 announcement](https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report), [report page](https://dora.dev/dora-report-2025/) and [Streamlining change approval](https://dora.dev/capabilities/streamlining-change-approval/)
- [Onnasch et al.](https://depositonce.tu-berlin.de/items/7df9879f-d77b-4f2b-8760-f0e3d174ca67), [Parasuraman and Manzey](https://depositonce.tu-berlin.de/handle/11303/8923), [Goddard et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC3240751), [Akhawe and Felt](https://www.usenix.org/conference/usenixsecurity13/technical-sessions/presentation/akhawe), [Anderson et al.](https://scholarsarchive.byu.edu/facpub/1955), [Buçinca et al.](https://arxiv.org/abs/2102.09692)
- [Hanley and Lippman-Hand](https://pubmed.ncbi.nlm.nih.gov/6827763/), [Newman](https://jamanetwork.com/journals/jama/article-abstract/389714)

**Vendor guidance and data**

- [AWS Scoping Matrix](https://aws.amazon.com/ai/security/agentic-ai-scoping-matrix/) and [Four security principles](https://aws.amazon.com/blogs/security/four-security-principles-for-agentic-ai-systems/)
- [Meta, Agents Rule of Two](https://ai.meta.com/blog/practical-ai-agent-security/)
- [Microsoft AI Red Team update](https://www.microsoft.com/en-us/security/blog/2026/06/04/updating-taxonomy-failure-modes-agentic-ai-systems-year-red-teaming-taught-us/)
- [Google's guidance for agent use](https://storage.googleapis.com/gweb-research2023-media/pubtools/1018686.pdf)
- [OpenAI, Practical guide](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf) and [Guardrails and human review](https://developers.openai.com/api/docs/guides/agents/guardrails-approvals)
- [Anthropic, Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode), [Harness design for long-running apps](https://www.anthropic.com/engineering/harness-design-long-running-apps), [Code migrations](https://claude.com/resources/articles/ai-code-migration) and [Verification loops](https://claude.com/resources/articles/building-verification-loops-in-claude-code-with-skills)
- [Horthy, Why Software Factories Fail](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/wsff.md) and [SlopCodeBench run](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/benchmarking-opus-5-on-slop-code-bench.md), from a vendor in this space. The benchmark's own [paper](https://arxiv.org/abs/2603.24755) was read as an abstract
