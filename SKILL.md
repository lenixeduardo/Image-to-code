---
name: image-to-code
description: Reconstruct a responsive webpage or UI from a supplied screenshot, mockup, or image. Use for image-to-code, screenshot-to-React, pixel-perfect implementation, asset extraction, layer decomposition, design-token and typography inspection, icon recovery, and visual QA across mobile, tablet, and desktop. Do not use for a textual feature request without a visual reference.
license: MIT
compatibility: Requires image-capable reasoning and access to a project workspace. Python 3.10+ and Pillow are optional for deterministic cropping/comparison; Playwright is optional for screenshot capture. Image generation, OCR, vector tracing, and font lookup require separate capabilities when needed.
---

# Image to Code — Layer-first Reconstruction

**Author and project creator:** Lenix Eduardo Rotundo de Camargo (GitHub: [@lenixeduardo](https://github.com/lenixeduardo)).

The project attribution above identifies the skill's creator. It does not transfer rights to third-party screenshots, logos, typefaces, or artwork reconstructed using this skill.

Convert a visual reference into working, accessible, responsive UI **without redesigning the source**. Work from large layers to small details. Preserve existing project conventions and user-provided assets. Never report inferred properties as measured facts.

## Inputs and precedence

1. Locate the reference image(s) and identify the target repository, framework, page route, and existing design system. Inspect the existing project before choosing new dependencies. Default to its current stack; use React/Next.js + TypeScript + CSS/Tailwind only if appropriate and not contradicted by the project.
2. Prioritize user-approved images/assets and explicitly provided instructions over screenshot approximation, then reliable image evidence, then documented responsive inference.
3. If only one viewport is provided, treat its geometry as **observed** only for that viewport. Infer other breakpoints and label them **inferred**; don't claim pixel-perfect fidelity on unseen screens.
4. Never replace a real brand logo, person's photograph, illustrated subject, product shape, or supplied graphic with an invented one. Exact crops do not reconstruct portions concealed by UI.

## Mandatory pipeline (in this order)

### 1. Inventory and normalize

- Record image filename, actual pixel dimensions, device pixel ratio if known, crop status, source viewport if known, and whether the image is a full-page or viewport screenshot.
- If tools are available, run `python scripts/image_inventory.py path/to/reference.png --out artifacts/inventory.json`. Its color samples are candidate values, **not** automatically the intended brand palette.
- Inspect visual references directly; never rely on OCR alone to recover text, fonts, or UI meaning. Document ambiguous details explicitly.

### 2. Decompose layers — back to front

Identify and inventory each meaningful region by bounding box, stacking order, repeat behavior, occlusion, and ownership. Use `references/layer-analysis.md`.

Process strictly:

1. **Background** — solid colors, gradients, texture, noise, overlays, backgrounds by section, fixed/scroll/parallax behavior. Rebuild via CSS where possible; export only genuine isolated raster artwork. Do not treat the complete screenshot as a usable clean background.
2. **Section layout and containers** — page frame, grid/flex, columns, gutters, max-width, alignment, padding, section height, breakpoints and stacking context.
3. **Components** — header/nav, hero, CTA, cards, buttons, fields, galleries, footer; identify states, constraints, focus/hover/tap behavior, ordering, semantics.
4. **Typography** — text hierarchy, candidate font families, weights, sizes, line heights, letter spacing, transformations, wrapping and exact copy. An image alone usually cannot prove the original font family; label confidence and use only legally accessible fonts.
5. **Icons and graphical assets** — preserve original icons or extract them with transparency if truly separable; if recreation is required use coherent SVG geometry and stroke. Don't silently substitute unrelated icons.
6. **Images and illustrations** — identify original files if available, otherwise extract only unobscured source pixels. Record crop, focal point, object-fit, aspect ratio, overlays, responsive art direction.
7. **Foreground microdetails** — separators, borders, shadows, blur, glow, decorative marks, overlays and motion.

Track everything in a **layer manifest** with observed/inferred/unknown classification. Use `scripts/export_layers.py` with explicit regions for safe pixel crops. Its outputs are screenshots fragments, not magically recovered originals. Do not invoke external image generators without a supported tool and permission/appropriate user context.

### 3. Produce a reproducible design specification

Before code, write `artifacts/design-spec.json` (see `references/design-spec.schema.json` and `references/spec-guide.md`), plus `artifacts/asset-manifest.json` and `artifacts/assumptions.md`.

Include:

- palette in HEX/RGBA, gradients/stops, opacity, shadows, borders, radii, spacing scale, grid/container widths, z-index;
- each font candidate, fallback, source/license, weights, font size, line height, letter spacing, and text treatment for desktop/tablet/mobile;
- every component's reference bounds, CSS role, states, min/max size, padding, alignment, stacking and behavior;
- every icon/image asset's location or generation requirement, license, transparency, crop and dimensions;
- named breakpoints and behavior rules **for mobile, tablet, desktop**;
- evidence classification (`observed`, `inferred`, `unknown`) and confidence (`high`, `medium`, `low`) for material decisions.

Use fluid CSS (`clamp`, `%`, `minmax`, `aspect-ratio`, `object-fit`) where it matches source evidence. Avoid arbitrary fixed heights and absolute positioning for primary layout; use absolute positioning only for genuinely overlaid elements. Validate spec with `python scripts/validate_spec.py artifacts/design-spec.json`.

### 4. Export and organize assets

**Mandatory source-asset audit for an existing project:** run `python scripts/audit_project_assets.py --project /path/to/project --out artifacts/project-assets.json` before implementation, and repeat it before acceptance. This catches static references to missing images even if an `onError` fallback makes the page appear visually intact. Missing approved source assets are blockers; do not silently fabricate, replace, or mark the output pixel-perfect.

- Store generated or extracted page assets under the project's preferred static directory (e.g., `public/assets/image-to-code/`), named by function: `hero-background.webp`, `hero-subject.png`, `logo.svg`, `icon-menu.svg`, etc.
- Export raster sources at original fidelity. Don't upscale and claim added detail. Use vector only when the shape is legitimately recoverable. Maintain transparent backgrounds for isolated foreground assets.
- Avoid cropping text into bitmap assets if it should be selectable/accessibly rendered as HTML.
- Use local provided assets first. Respect copyright/license for external fonts/photos/icons, and record asset provenance.
- Where occluded content is impossible to recover, list a missing asset and **do not silently synthesize**.

### 5. Implement with responsive components

- Build semantic, reusable component tree; define theme tokens and typography first, then background, layout, components, icons/images, and microdetails in that order.
- Keep desktop/tablet/mobile behavior explicit in the spec: navigation collapse, card columns, reflow/reorder, image crop, text scaling, touch interaction, modal behavior, overflow, spacing, hidden/visible elements.
- Use breakpoints based on observed design shifts rather than a dogmatic device-size assumption. Default inspection sizes: **390×844**, **820×1180**, **1440×900**; also smoke-test **360, 430, 768, 1024, 1280, 1920px** widths.
- Include keyboard navigation, focus-visible, accessible names, reduced motion, image alt text, layout stability, touch targets and avoidance of horizontal overflow.
- Avoid replacing existing source assets or unrelated project files; scoped edits only. Avoid adding unnecessary frameworks, fonts and icon libraries.

Read `references/responsive-rules.md` and `references/implementation-guide.md` during this step.

### 6. Validate visually; iterate

1. Run project lint/build/tests where available; inspect console and runtime errors. Also run `python -m unittest discover -s tests -v` and `node --test tests/test_capture.mjs` for changes to this skill; these checks verify the tooling, not UI fidelity.
2. Render **desktop, tablet, and mobile screenshots**, plus matching original viewport and intermediate widths, using browser automation, e.g. `node scripts/capture.mjs --url http://localhost:3000 --out artifacts/screenshots --reference-viewport 1179x616 --smoke-widths 360,430,768,1024,1280,1920` after installing Playwright. Record screenshots and `capture-report.json` in the final deliverables; fail quality gates on broken images, JavaScript errors, unlabeled interactive controls, horizontal overflow or missing main landmark. Do not pass `--allow-warnings` for approval. **Embed the required side-by-side boards visibly in the chat** when the interface supports it; never substitute download links for in-chat evidence.
3. For each supplied reference and matching viewport: run `python scripts/audit_visual.py --reference input.png --render artifacts/screenshots/desktop.png --out artifacts/audit/desktop`. Sizes must match; if they do not, correct the viewport rather than silently resize.
4. Review geometry, font rendering, assets, colors, spacing, responsive behavior and interactions manually. Fix the largest divergences, re-capture, and compare again. Treat automated pixel error as a **diagnostic**, not an authoritative visual quality score. See `references/visual-qa.md`.
5. Produce the **mandatory presentation boards** via `scripts/present_results.py`, and show both **directly inside the chat**, not just as downloadable links: mobile + tablet side-by-side; if the source reference is a desktop UI screenshot, original desktop + rebuilt desktop side-by-side. Never use a single giant multi-device collage. If source and render are not the same viewport, disclose the mismatch and recapture before a fidelity claim. Consult `references/presentation-standard.md`.
6. Target **≥9.5/10 on every viewport that has a reference**, with screenshot evidence and the weighted rubric. For inferred breakpoints, report responsive quality separately, not pixel fidelity. If target cannot be reached, report exact deviations and evidence instead of claiming success.

## Mandatory fidelity contract and multi-agent rejection gates (v1.4.0)

**Read [fidelity-gates.md](references/fidelity-gates.md) and run its two specialist reviews plus an independent acceptance review before reporting success.** Use distinct agents when the runtime supports them; otherwise perform three clearly documented separate review passes. Never represent a role-based manual pass as an actually spawned agent.

- **Agent A, UI fidelity:** inspect original icons rather than swapping icon libraries; verify the actual loaded font, computed CSS and glyphs; compare button size/position/padding with independently measured reference XYWH. A larger CTA is a failed gate even if the global screenshot diff is low.
- **Agent B, asset integrity:** preserve the approved original subject and embedded glow as one composite when baked together. Forbid regenerating it, artificial upper/lower blur, extra CSS halos and clipped subject details. Verify extremities (including a cat's paw) as dedicated regions. A cropped screenshot derivative does not count as the lost original.
- **Agent C, acceptance:** review A and B evidence, run browser interactions, independently compare each critical region and check protected asset hashes. Reject altered icons, font fallback, CTA-size deviations, missing details and unverified visual claims.
- **Run the strict contract gate:** `python scripts/audit_fidelity_contract.py --contract artifacts/visual-fidelity.contract.json --project . --out artifacts/audit/fidelity-contract-report.json`. Start from the example JSON and **replace all sample coordinates** with actual measured screenshot regions, add immutable original asset hashes, and enable `require_protected_assets` for pages with approved source art. Do not change thresholds after seeing failures to force acceptance.
- Treat user-reported visual defects as **separate, blocking regression cases**: icon shape, typography, CTA geometry, upper/lower glow boundaries and all visible subject details. Never average a critical failure away in the total score. Do not claim ≥9.5 while any unresolved blocking regression remains.
- Reference and render must be captured at matching viewport/DPR, with fonts/images loaded and relevant states matched. This gate does not substitute for a real browser, human visual review or in-chat evidence boards.

## Required output contract

Return a project-ready implementation, **not just a text prompt**:

- Actual source-code changes and any required extracted assets, or an explicit blocker where tool support is absent.
- `artifacts/design-spec.json`, `artifacts/asset-manifest.json`, `artifacts/assumptions.md`, and an audit report.
- A concise component tree, font scale in px/rem, design tokens, image/icon manifest, and breakpoint table.
- **Mandatory chat-visible images:** one mobile + tablet side-by-side board; one desktop original + reconstruction side-by-side board when the user supplied a desktop-interface screenshot. For a non-desktop reference, show the desktop preview separately. These must render directly in the conversation, with links only as secondary downloads. Keep both panels readable, labeled, entirely visible and undistorted. Record reference cropping/viewport differences; do not present inferred layouts as faithfully matched.
- Screenshot evidence for mobile/tablet/desktop, test/build outcomes, and a separate score per reference viewport.
- A clear distinction between **confirmed from image**, **inferred for responsiveness**, and **not recoverable**.

Never claim assets were created, screenshots captured, tests passed or a page was deployed unless those outputs actually exist. Do not treat analysis-only completion as completed image-to-code implementation.

## Supporting files

- [Layer decomposition and extraction](references/layer-analysis.md)
- [Design spec JSON schema](references/design-spec.schema.json)
- [Spec examples and evidence rules](references/spec-guide.md)
- [Responsive behaviors](references/responsive-rules.md)
- [Implementation rules](references/implementation-guide.md)
- [Visual QA and acceptance](references/visual-qa.md)
- [Mandatory demonstration format](references/presentation-standard.md)

## Acceptance integrity (v1.1.0)

- A tool test passing is not proof of a faithful reconstructed website. A full QA report needs an actual browser render, comparison at matching viewport/DPR and user-visible evidence boards.
- Browser runtime checks include failed/broken images, interactive controls without accessible names, JavaScript console errors, missing `main`, horizontal overflow and failed requests. Investigate rather than blanket ignoring failures.
- In screenshot audits, any excluded dynamic regions must be explicit, limited in scope and **visible as neutral masks** in diagnostics. Never use large masks to hide defective artwork.
- Never assign a perfect 10/10 to the skill or a reconstructed page when end-to-end browser execution is blocked or when referenced viewports and fonts cannot be validated. Document unresolved gaps by severity.

- For desktop screenshot QA, invoke `scripts/present_results.py` with `--require-matching-desktop` to make mismatched dimensions a failed acceptance gate, not just a warning.