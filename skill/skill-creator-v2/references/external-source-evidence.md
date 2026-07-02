# External Source Evidence

Use this reference when creating or improving skills that rely on external sources: web research, design references, SEO/SERP work, market research, legal/regulatory checks, documentation lookup, product recommendations, current tool/library advice, or any workflow where facts can be stale or hallucinated.

Do not force this reference onto purely local coding skills, tiny edits, or explicit vibe-mode drafts. In vibe mode, disclose which evidence gates were skipped and do not claim production readiness.

## External Source Evidence Ladder

Define the smallest ladder that fits the domain. Default ladder:

1. `source_taxonomy_defined`: source classes and accepted source types are named.
2. `candidate_source_identified`: a possible source was found.
3. `source_page_opened`: source page, document, API result, or user-provided artifact was opened/read.
4. `primary_content_read_or_captured`: relevant content was read, extracted, screenshotted, or otherwise captured.
5. `supporting_artifact_saved`: raw evidence path, URL, screenshot, JSON, transcript, or report was saved or cited.
6. `metadata_or_context_inspected`: timestamp, freshness, author/source type, DOM/API metadata, publication date, version, license, or context was checked when material.
7. `claim_mapped_to_evidence`: every important claim maps to an artifact or source.
8. `project_fit_or_user_fit_reviewed`: evidence was checked against the user's project, audience, jurisdiction, product type, risk level, or constraints.
9. `staleness_and_confidence_labeled`: confidence and freshness/staleness are stated.
10. `accepted_evidence`: source evidence is sufficient for the claimed output.

`candidate_source_identified`, `taxonomy_only`, `catalog_card_seen`, hero-only screenshots, or source names without opened/read evidence are not accepted evidence.

## External Source Skill Contract

External-source skills must define:

- source classes and source priority;
- accepted source evidence levels;
- required artifact paths or citation format;
- source freshness/staleness policy;
- confidence labels;
- failure labels;
- fallback behavior;
- no-copy or usage-rights rules when third-party material is involved;
- conditions that downgrade output to `partial_output`, `manual_review_required`, or `not_run`.

## Source Status Labels

Use source status labels consistently in reports, evals, and final review.

Use labels such as:

- `verified`: source opened/read and artifact recorded.
- `assumed`: source type is plausible but not directly verified in this run.
- `taxonomy_only`: only category/source taxonomy was used.
- `catalog_card_seen`: listing/card/source shell was seen but primary content was not reviewed.
- `partial_output`: some evidence exists but required evidence is missing.
- `manual_review_required`: human or account/tool access is required before acceptance.
- `not_run`: the required live/source check was intentionally or necessarily not executed.
- `stale_data`: source may be outdated or freshness could not be verified.
- `hallucinated_source`: output claimed evidence that was not actually opened/read.

## Confidence And Freshness

Every important external claim should state:

- source name or artifact path;
- checked date or source date when available;
- confidence: high / medium / low;
- freshness: current / likely-current / stale-risk / stale;
- downgrade reason when confidence is not high.

For legal, medical, financial, regulatory, current product, package, API, pricing, schedule, or public-person/company facts, treat freshness as high-risk and require current verification.

## Shallow Evidence Anti-Pattern

Reject or downgrade:

- source named but not opened/read;
- search result snippet treated as full source;
- catalog/listing card treated as reviewed source;
- hero screenshot treated as full visual review;
- visual review without `scroll_sequence_captured`, `interaction_captured`, screenshot series, or an explicit reason the page cannot be scrolled/interacted with;
- source artifact path missing;
- source date/freshness absent for time-sensitive claims;
- copied third-party code/assets/text/layout;
- generated output that cites planned commands or invented artifacts.

## Completion Vs Acceptance

External evidence is not accepted because a worker finished or a file exists.

Acceptance requires:

1. the required evidence level was reached;
2. artifacts or citations exist;
3. important claims map to evidence;
4. freshness/confidence labels are present;
5. shallow-evidence anti-patterns are absent;
6. independent verification or review passed when the output is production-grade.

## Template Fields

Generated skills should include fields like:

```markdown
## External Source Evidence Contract
- Source classes:
- Required evidence level:
- Artifact paths:
- Freshness policy:
- Confidence labels:
- Failure labels:
- Fallback behavior:
- Do-not-copy / rights policy:
- Acceptance gate:
```

## 9+/10 Rule

An external-source skill cannot score 9+/10 unless it has:

- an External Source Evidence Ladder;
- an External Source Skill Contract;
- shallow-evidence rejection;
- confidence and staleness handling;
- artifacts or citations for important claims;
- a simple-task skip rule when the external-source workflow would be overprocessing.
