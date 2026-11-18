# Shared Engineering Quality & Release Governance v1.1

**Scope:** Reusable engineering baseline for GitHub projects. Project-specific policies take precedence only when explicitly documented. This document does not assert that any repository already meets these controls.

## 1. Source changes and verification (P0)

- Inspect the current source and its exact path before modifying it.
- Require edit anchors to exist; reject replacements that make no content change.
- After writing, fetch the file again and verify intended lines, content hash, and commit SHA.
- Never equate a successful API write with functional validation.
- Keep each change small, reversible, and attributable to a commit.

## 2. Evidence-based reporting (P0)

Report separately: **Implemented** (source present), **Executed** (test actually ran), **Passed** (observed success), **Validated** (relevant environment and acceptance criteria), and **Released** (authorized distribution). Missing evidence is **Pending**, never presumed passing. Associate CI run URLs and results with the exact commit. State blockers and next actions without inflating maturity.

## 3. Tests and release promotion (P0)

- Choose appropriate static checks, unit, integration, end-to-end, and platform tests for the product.
- Release artifact promotion must depend on successful applicable checks, not merely ZIP/build success.
- Record the required jobs and their actual execution status. An uploaded artifact alone is not release approval.
- Keep a manual acceptance checklist for behavior CI cannot establish.

## 4. Reproducible and auditable distribution (P1)

- Build from a documented, allowlisted manifest when packaging distributable files.
- Reject unexpected paths, symlinks, missing files, and non-approved inputs.
- Normalize timestamps and permissions where practical; repeat builds and compare SHA-256 hashes.
- Publish or retain checksums with exact commit and run evidence.
- Validate the **extracted deliverable**, not only the source checkout.
- Confirm that quick-start commands actually exist in the delivered package.

## 5. Privacy, security, and publication (P1)

- Exclude secrets, personal files, credentials, environment-specific paths, and production records.
- Scan tracked files and inspect repository history before making anything public; automated scanning is a baseline only.
- Keep demonstration data fictional or verified sanitized, and clearly distinguish simulated from connected/live capabilities.
- Do not make a repository public, create a release, contact external parties, or post an announcement without the owner's explicit authorization.
- Keep private artifacts and screenshots access-controlled and short-lived.

## 6. Maturity and operations

Preserve the existing maturity tiers: **T1** local deterministic; **T2** integration readiness; **T3** operational validation; **T4** production survivability. Do not mix tiers or claim higher maturity without evidence. Preserve offline behavior, deterministic tests, traceability, recovery paths, and platform-specific safeguards where relevant.

## 7. Project adoption checklist

- [ ] Review current architecture, build system, CI, test suite, and privacy boundaries.
- [ ] Identify applicable controls and document justified exceptions.
- [ ] Add only missing checks; do not replace functioning project-specific workflows.
- [ ] Run tests on the actual target environment and record evidence.
- [ ] Update setup/release docs to match shipped files.
- [ ] Record commit, CI run, package hash (if applicable), unresolved issues, and owner decision.

**Status of this document:** Standard defined; adoption and compliance are separate per-repository decisions.
