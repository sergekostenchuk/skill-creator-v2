# Figma Operation Archetype

Use this reference when Figma canvas, components, tokens, or design-system state are central to the task.

Figma is usually a `tool_surface`, not a top-level class. A skill becomes a Figma operation skill only when it must read or change Figma artifacts and verify the result in Figma terms.

## Use This Archetype When

Use `derived_archetype: figma_canvas_operation` when the skill must:

- create, edit, or validate nodes on a Figma canvas;
- read back node IDs, frame hierarchy, component instances, variants, tokens, or styles;
- synchronize design-system tokens/components;
- translate between Figma and code;
- apply effects, motion, or layout changes directly in Figma;
- produce before/after screenshots or export evidence.

## Do Not Use It When

Do not use Figma operation when:

- Figma is only mentioned as a future destination;
- the task only writes a design brief;
- the skill produces code without reading or writing Figma;
- no node/readback/canvas evidence is expected.

## Classification Tuple

Typical tuple:

```json
{
  "activity_type": ["build", "transform", "validate"],
  "domain": ["design_ux", "design_system"],
  "tool_surface": ["figma"],
  "risk_profile": {
    "primary": "visual_client_facing",
    "secondary": ["internal_reversible"]
  },
  "evidence_profile": ["generated_artifact", "screenshot", "before_after_comparison", "trace_log"],
  "workflow_shape": ["sequential_pipeline", "independent_reviewer"],
  "derived_archetype": "figma_canvas_operation"
}
```

## Required Evidence

Minimum evidence:

- `generated_artifact`: Figma file/frame/node IDs or exported artifact.
- `before_after_comparison`: before/after node state, screenshot, or export.
- `trace_log`: tool calls or operations performed.
- `visual_review`: screenshot review for layout, hierarchy, text fit, and fidelity.

For design-system work, add component/token diff evidence.

## Example Prompt Classification

Prompt: "Take the approved website direction and create a Figma frame with matching components and token styles."

Classification:

- activity: `build`, `transform`, `validate`
- domain: `design_ux`, `design_system`
- tool surface: `figma`
- risk: `visual_client_facing`, `internal_reversible`
- evidence: `generated_artifact`, `screenshot`, `before_after_comparison`, `trace_log`, `visual_review`
- route: `deep` when output is client-facing or part of a design-system pipeline

## Verification Rules

- Read back created or edited node IDs.
- Verify frame hierarchy and key properties.
- Capture before/after screenshots or exports where possible.
- Do not claim Figma success from prose alone.
- Escalate when the Figma tool is unavailable or cannot read back the changed state.
