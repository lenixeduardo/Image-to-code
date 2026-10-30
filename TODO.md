# Image to Code — Improvement backlog

Status as of 2026-10-30. This is the skill's engineering backlog, **not** a list of defects already fixed. P0 blocks high-fidelity claims.

## P0 — acceptance blockers

- [x] Add per-state pixel calibration, explicit viewport/normalization controls, labeled comparison images, SSIM (optional), MAE and difference maps.
- [x] Add browser state/geometry validation to detect clipped phone frames and hidden critical UI that text-presence tests miss.
- [x] Require a multi-state character/expression audit and preserve approved artwork, lighting, icon and exact mockup copy in the skill instructions.
- [ ] Benchmark three **independent** real-world projects with approved, non-derived mobile/tablet/desktop references and publish anonymized evidence plus false-positive rate.
- [ ] Verify the full pipeline autonomously with an image-capable coding agent, including assets, HTML/CSS build, browser render, correction loop and reproducible visual evidence (not only auxiliary scripts).
- [ ] Recover the separate high-resolution Catty character/scene source layers where available. Crops from flattened screenshots cannot reconstruct paws or artwork hidden behind UI exactly; document as unresolved, never invent proof.

## P1 — quality and interoperability

- [ ] Add optional perceptual alignment hints (edge/landmark registration), but do not shift/warp source without an explicit audit trail.
- [ ] Add component-level geometry tolerance config and thresholds by semantic priority (face/CTA/layout/icons), preserving a hard default no-clipping gate.
- [ ] Automate font metadata comparison when licensed font files are available, including actual browser font fallback detection and text-wrap differences.
- [ ] Add mask-aware SSIM and per-region perceptual scores, enforce mask size ceilings to prevent hiding errors.
- [ ] Implement visual tests of restored icons vs original vector geometry (outline weight, filled style, baseline).
- [ ] Test the installer and skill invocation end-to-end on Claude Code, Codex, OpenCode, Hermes, Freebuff/Codebuff, Cursor and other supported agents; do not claim external CLI testing without evidence.
- [ ] Test swipe/touch and focus order on iOS Safari/WebKit and Android Chromium (current evidence mostly Chromium desktop engine).

## P2 — ergonomics and publication

- [ ] Generate a compact machine-readable per-component CSS change proposal from visually measured deltas, **reviewed** before applying.
- [ ] Add a Markdown dashboard linking each state reference, render, heatmap, metrics and QA logs.
- [ ] Add an interactive visual overlay inspector in the browser that does not modify the approved reference.
- [ ] Track visual calibration history in CI artifacts for regression analysis without uploading proprietary screenshots to a public repository.

## Evidence rules

- A passing script suite is **tool reliability**, not fidelity of a generated UI.
- Perceptual similarity metrics (SSIM / MAE) are diagnostics, **not** the 0–10 score.
- Refuse final approval whenever required UI elements are clipped, source assets are silently replaced, or a screenshot is not produced by a real browser.
