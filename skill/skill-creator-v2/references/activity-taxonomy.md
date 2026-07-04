# Activity Taxonomy

Use this reference when a skill request needs classification beyond the simple request mode. The purpose is to identify the human work being turned into agent instructions, not to assign one flat class name.

The canonical output is a multi-axis tuple:

- `activity_type`: what the agent does.
- `domain`: professional subject matter.
- `tool_surface`: where the agent reads, writes, observes, or acts.
- `risk_profile`: why mistakes matter.
- `evidence_profile`: what proves the work was done correctly.
- `workflow_shape`: how work is coordinated over time.
- `catalog_family`: optional navigation bucket.
- `specialist_role`: optional human role/vocabulary.
- `derived_archetype`: reusable named combination for templates and evals.

Do not use catalog family, role, or tool name as the canonical class. They help routing, but gates come from risk and evidence.

## Required Axes

### `activity_type`

Allowed values:

- `research`: find and collect information from sources.
- `analyze`: interpret evidence, compare options, or diagnose a state.
- `design`: define a plan, architecture, direction, schema, workflow, or concept.
- `build`: create a new artifact or implementation.
- `transform`: convert, migrate, ingest, normalize, or refactor existing material.
- `configure`: change settings, configs, DNS, certificates, routes, tools, or environments.
- `operate`: run a system, perform routine actions, or execute an established procedure.
- `troubleshoot`: find and fix a failure.
- `validate`: test, audit, review, benchmark, or check compliance.
- `defend`: prepare a position under adversarial, legal, administrative, or dispute conditions.
- `orchestrate`: coordinate multiple skills, workers, tools, or stages.
- `publish_release`: package, deploy, release, or distribute.
- `monitor`: observe over time and trigger follow-up actions.
- `communicate`: draft, reply, summarize, or structure communication where communication is the output.

If more than two high-substance activities are required, evaluate whether the output should be a skill group.

### `domain`

Allowed values:

- `infrastructure`: servers, hosting, system packages, storage, OS/runtime state.
- `network_vpn`: VPN, Xray, routing, tunnels, private networking, routers, network devices.
- `dns_ssl_domain`: domains, DNS, SSL/TLS, ACME, registrar/Search Console setup.
- `deployment_devops`: CI/CD, release, deploy, health checks, rollback.
- `security`: threat modeling, hardening, appsec, privacy, incident response.
- `legal`: legal, tax, traffic, administrative defense, compliance, jurisdiction-specific reasoning.
- `design_ux`: UI/UX, visual direction, interaction, usability, design critique.
- `design_system`: tokens, components, design-to-code/code-to-design synchronization.
- `seo_discoverability`: SEO, LLM discoverability, semantic core, schema, authority, SERP evidence.
- `wiki_knowledge`: ingest, query, lint, cross-link, synthesis, knowledge graph maintenance.
- `browser_web`: live website inspection, DOM/network analysis, screenshots, web interaction.
- `media_creative`: image, video, motion, animation, generated media.
- `skill_meta`: creating, evaluating, hardening, packaging, publishing, or governing skills.
- `data_document`: spreadsheets, documents, PDFs, structured conversions, reports.
- `desktop_app`: Tauri, sidecars, local app operations, desktop automation.

Domain alone must not decide gates. Gates come from `risk_profile` and `evidence_profile`.

### `tool_surface`

Allowed values:

- `filesystem`
- `terminal`
- `server_ssh`
- `network_device_cli`
- `browser`
- `external_website`
- `figma`
- `api_mcp`
- `package_manager`
- `git_github`
- `legal_sources`
- `design_tools`
- `database_query`
- `cloud_provider`
- `desktop_gui`
- `image_video_tooling`

Tool names are surfaces, not top-level skill classes. If a tool surface can modify production or private state, the risk profile must not stay low.

### `risk_profile`

Allowed values:

- `low_advisory`: reversible advice, planning, or local draft output.
- `internal_reversible`: local or internal changes that can be reverted from diff/history.
- `external_source_freshness`: relies on current external sources, live sites, search, pricing, law, or changing docs.
- `visual_client_facing`: output will be judged visually or commercially.
- `production_infrastructure`: may affect live systems, access, uptime, DNS, SSL, routing, deployment, or server state.
- `security_privacy`: may affect credentials, privacy, attack surface, routing privacy, permissions, or supply chain.
- `legal_high_stakes`: legal/tax/traffic/administrative conclusions, filings, defense strategy, deadlines, or jurisdiction-specific claims.
- `financial_business`: may influence material spend, business decision, client acquisition, pricing, or paid campaigns.
- `irreversible_destructive`: deletion, destructive migration, non-reversible write, account risk, public publication, or production lockout risk.

When risk confidence is low, default upward and require review.

### `evidence_profile`

Allowed values:

- `command_output`
- `config_diff`
- `test_result`
- `screenshot`
- `dom_metadata`
- `network_log`
- `source_citation`
- `legal_citation`
- `source_hash`
- `package_hash`
- `benchmark_metric`
- `human_approval`
- `before_after_comparison`
- `rollback_proof`
- `generated_artifact`
- `visual_review`
- `trace_log`
- `decision_packet`

Evidence is a contract, not a tag. Each required evidence item should specify path, collection method, validator, owner, and sanitation rule.

### `workflow_shape`

Allowed values:

- `single_pass`: one bounded pass, no loop expected.
- `iterative`: repeat until quality threshold or loop limit.
- `sequential_pipeline`: fixed ordered stages.
- `branching_pipeline`: conditional routes based on observations.
- `orchestrator_worker`: coordinator delegates to worker skills.
- `independent_reviewer`: separate review/judge stage validates output.
- `evaluator_optimizer`: produce, evaluate, revise loop.
- `monitoring_loop`: recurring or watch-based workflow.
- `parallel_research`: independent parallel research lanes reconciled later.
- `human_decision_gate`: explicit human selection point inside a larger workflow.

Group workflows must define handoff contracts and context-review checkpoints between workers.

## Optional Navigation Axes

Use `catalog_family` for package organization only: `engineering`, `networking`, `legal`, `design`, `growth`, `knowledge`, `media`, `meta`, `operations`.

Use `specialist_role` to select vocabulary and reviewers, for example `devops_engineer`, `network_admin`, `security_analyst`, `lawyer`, `tax_defense_specialist`, `traffic_defense_specialist`, `designer`, `figma_operator`, `seo_specialist`, `knowledge_manager`, `release_manager`, `skill_architect`.

## Derived Archetypes

Derived archetypes are named axis combinations for examples, templates, and eval fixtures. They are not the primary taxonomy.

| Archetype | Typical Tuple | Evidence/Gate Fingerprint |
| --- | --- | --- |
| `server_provisioning` | configure/build + infrastructure + server_ssh/terminal + production_infrastructure | SSH output, service status, config diff, rollback proof. |
| `private_network_operation` | design/configure/validate + network_vpn + terminal/server_ssh/filesystem + security_privacy/production_infrastructure | Tunnel status, routing table, leak test, config diff, rollback plan. |
| `network_device_operation` | configure/operate/troubleshoot + network_vpn + network_device_cli + production_infrastructure/security_privacy | Before config, route/ACL diff, connectivity check, lockout rollback. |
| `domain_dns_ssl_operation` | configure/validate + dns_ssl_domain + browser/api_mcp/terminal + production_infrastructure/external_source_freshness | DNS lookup, SSL validation, propagation notes, registrar record diff. |
| `deployment_release_operation` | publish_release/validate + deployment_devops + terminal/git_github/server_ssh/api_mcp + production_infrastructure | Build/test log, deploy log, health check, rollback proof. |
| `legal_reasoning_and_defense` | research/analyze/defend/communicate + legal + legal_sources/browser/filesystem + legal_high_stakes | Jurisdiction, matter type, citation, source date, decision packet, human approval. |
| `ui_reference_research` | research/analyze + design_ux + browser/external_website + external_source_freshness/visual_client_facing | Screenshots, source URLs, DOM/tech notes, pattern extraction, originality guard. |
| `ui_build` | design/build/validate + design_ux + filesystem/browser/terminal + visual_client_facing | Screenshots, viewport checks, visual review, usability caveats. |
| `figma_canvas_operation` | build/transform/validate + design_ux/design_system + figma + visual_client_facing | Node IDs, before/after screenshots, component/token diff. |
| `seo_semantic_core` | research/analyze/design/validate + seo_discoverability + browser/api_mcp/external_website + external_source_freshness/financial_business | Source citations, SERP evidence, keyword tables, schema validation. |
| `browser_live_inspection` | analyze/validate + browser_web + browser/external_website + external_source_freshness | Screenshots, DOM snapshot, network log, loading notes, interaction trace. |
| `wiki_knowledge_ingest` | transform/validate + wiki_knowledge + filesystem/api_mcp/browser + low_advisory/internal_reversible | Manifest, source hash, link checks, before/after diff. |
| `media_motion_generation` | design/build/validate + media_creative + image_video_tooling/filesystem/terminal/api_mcp + visual_client_facing | Rendered artifact, frame/video review, prompt/source record, hash. |
| `skill_meta_creation` | research/design/build/validate/orchestrate + skill_meta + filesystem/terminal/git_github/package_manager + security_privacy/low_advisory | SKILL.md, references, lint/evals, package hash, behavioral eval output. |

## Anti-Patterns

Reject these classification shortcuts:

- `Figma` as a top-level class.
- `browser` as the class for every web task.
- `security_legal_compliance` as one bucket.
- `infra` as one bucket for VPS, router, DNS, Xray, and deployment without subclass evidence.
- `lawyer` as a class instead of a specialist role.
- `human_in_loop` as a replacement for risk analysis.
- `done` based on generated text without evidence.
- group creation only because a workflow has many steps.

Use `references/browser-live-inspection.md` only when browser runtime behavior is central and requires DOM/session/network/screenshot evidence.

Use `references/figma-operation-archetype.md` only when Figma canvas, node, token, component, readback, or before/after evidence is required.

## Classification Notes

Start with the smallest truthful tuple. Add complexity only when risk, evidence, tool boundaries, or specialist roles require it.

If classification confidence is low on a core axis, do not silently choose a low-risk path. Produce a decision packet, ask for missing context, or block production/destructive actions until reviewed.
