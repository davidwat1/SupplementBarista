# Portfolio Engineering Standards — Operating Contract v1.0

**Owner intent:** Every new GitHub project inherits the portfolio engineering baseline automatically as a planning and implementation requirement. Improvements discovered in any project are evaluated for other repositories, including those not currently under active development.

**Important limit:** This is a reusable policy and bootstrap contract, not a background service. It does not by itself create repositories, install ChatGPT skills, trigger CI, or monitor other repositories without an invoked workflow or scheduled automation.

## 1. New-repository bootstrap — mandatory

Before first implementation, establish:

1. **Charter:** purpose, intended users, scope, exclusions, privacy classification, definition of done, and release authority.
2. **Architecture:** module boundaries, data flows, persistence, external dependencies, failure and recovery modes, observability, and threat/safety considerations.
3. **Development workflow:** repository structure, source control conventions, versioning, local setup (PowerShell on Windows when applicable), dependency locking, and configuration separation.
4. **Quality system:** deterministic unit tests, integration/contract tests, scenario and regression harnesses, coverage reporting appropriate to the project, and CI gates.
5. **Delivery system:** build/package manifest, reproducibility where practical, checksum verification, extracted-package smoke tests, deployment/rollback plan, and artifact retention.
6. **Documentation:** README, architecture, project delivery plan, decision log, setup instructions, test instructions, and release evidence.
7. **Governance:** human approval for external side effects, no secrets or private data in repo, explicit publication approval, and evidence-based maturity scoring.

Use `docs/engineering-quality-release-governance-v1.1.md` as the minimum quality and release standard. Do not assume a specific application language, framework, cloud provider, UI, or deployment target; select those based on the project's needs.

## 2. Project kickoff sequence

- Inspect existing repositories and reusable patterns before choosing architecture.
- Draft project-specific charter and architecture decisions.
- Create the repo **private by default**, unless the owner explicitly approves public visibility.
- Include the portfolio operating contract and quality standard with a version/reference.
- Create the baseline directory structure, tests, automation, and setup guide suitable for the selected stack.
- Run applicable tests and report evidence; do not claim passing or deployment before verification.
- Record exceptions and rationale instead of silently omitting controls.

## 3. Cross-repository learning loop

When a project reveals a new reusable practice, defect class, or architectural improvement:

1. Capture the finding with evidence and its originating repository/commit.
2. Classify it as **Mandatory**, **Recommended**, **Conditional**, or **Project-specific**.
3. Update the versioned portfolio standard when broadly applicable.
4. Inventory relevant repositories and record applicability, adoption status, owner, and risks.
5. Apply safe, nonbreaking improvements to other repositories when authorized and tools permit; run their own test suites.
6. Record **Not applicable**, **Deferred**, or **Blocked** explicitly. Do not claim all projects updated because a common document changed.

Evaluate dormant projects when touched, during a deliberate portfolio review, or through an explicitly configured automation. No background monitoring is implied by this document.

## 4. Evidence and maturity

Separate **Documented**, **Implemented**, **Executed**, **Passed**, **Validated**, and **Released**. A Git commit proves a file write, not runtime success. Associate results with exact commits and run IDs. Preserve T1 local deterministic, T2 integration readiness, T3 operational validation, T4 production survivability. Never inflate maturity.

## 5. Required starter documents

- `README.md` — purpose, verified capabilities, setup, test commands, limitations
- `docs/architecture.md` — components, interfaces, data boundaries, tradeoffs
- `docs/project-delivery.md` — milestones, risks, owners, evidence
- `docs/decisions.md` — architectural decision records and exceptions
- `docs/portfolio-adoption.md` — inherited standard version and compliance gaps
- `docs/engineering-quality-release-governance-v1.1.md` — shared quality baseline
- `.github/workflows/` — project-appropriate CI, not a copied workflow with irrelevant jobs

## 6. Release and external action policy

Do not publish a repository, issue a public release, post on LinkedIn, contact third parties, or connect real user accounts without explicit owner approval. Separate fictional demos from operational tools and personal data.

## 7. Portable kickoff instruction

> For this GitHub-backed project, first inherit the current Portfolio Engineering Standards operating contract and the shared Engineering Quality & Release Governance standard. Review existing portfolio patterns and identify project-specific deviations. Establish charter, architecture, tests, CI, documentation, privacy boundaries, maturity tier, and release gates before claiming delivery. Propagate broadly useful engineering improvements across other repositories through documented impact assessment and verified changes. Preserve existing systems; never equate committed code with tested or released software.

**Adoption:** Copy this file into each repo or link to a centrally maintained version. Version and review changes. The canonical location must be agreed and reachable; until then, copies in the repositories are a synchronized baseline, not a live inheritance mechanism.
