# Browser Live Inspection Archetype

Use this reference when the browser runtime itself is central to the task.

Browser is usually a `tool_surface`, not a top-level skill class. Ordinary web research, citation gathering, or reading documentation should not be classified as `browser_live_inspection` unless the task requires observing runtime behavior.

## Use This Archetype When

Use `derived_archetype: browser_live_inspection` when the skill must inspect:

- rendered layout across viewport states;
- DOM structure or runtime state;
- network requests, fonts, scripts, media, or loading behavior;
- interactions such as hover, cursor, scroll, reveal, animation, form behavior, or route transitions;
- screenshot sequences or visual diffs;
- accessibility/runtime metadata;
- live-site technology/effect behavior that cannot be seen from a catalog card.

## Do Not Use It When

Do not use browser live inspection when:

- the browser is only used to read a source;
- the task is static research with citations;
- the output is a written summary with no runtime claim;
- screenshots are optional decoration rather than evidence;
- the site cannot be accessed and no fallback evidence is available.

## Classification Tuple

Typical tuple:

```json
{
  "activity_type": ["analyze", "validate"],
  "domain": ["browser_web"],
  "tool_surface": ["browser", "external_website"],
  "risk_profile": {
    "primary": "external_source_freshness",
    "secondary": ["visual_client_facing"]
  },
  "evidence_profile": ["screenshot", "dom_metadata", "network_log", "trace_log"],
  "workflow_shape": ["iterative"],
  "derived_archetype": "browser_live_inspection"
}
```

## Required Evidence

Minimum evidence:

- `screenshot`: one or more screenshots with URL, viewport, timestamp, and interaction state.
- `dom_metadata`: title, URL, selected structure, font/script/style hints, and relevant element notes.
- `network_log`: request summary when load behavior, assets, effects, or performance are part of the claim.
- `trace_log`: scroll/hover/click/wait steps and observed state changes.

For design intelligence, include source status and originality notes. Do not copy proprietary code, layouts, images, text, SVGs, or unique animations; summarize principles and implementation clues.

## Example Prompt Classification

Prompt: "Look through an Awwwards winner, scroll through 3-5 screens, inspect hover effects and code hints, and save ideas for a yacht school."

Classification:

- activity: `research`, `analyze`, `validate`
- domain: `design_ux`, `browser_web`
- tool surface: `browser`, `external_website`
- risk: `external_source_freshness`, `visual_client_facing`
- evidence: `screenshot`, `dom_metadata`, `network_log`, `source_citation`, `decision_packet`
- route: `deep` if the output influences a production design direction

## Access Limits

Respect site access limits and source boundaries:

- label blocked, paywalled, rate-limited, or unreachable sources;
- avoid scraping beyond the task need;
- obey robots/access constraints where applicable;
- never store secrets, tokens, signed URLs, or private user data from browser traces;
- keep copyrighted/source code excerpts minimal and use summaries for implementation patterns.
