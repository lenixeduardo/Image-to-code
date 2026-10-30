# Image to Code — Backlog after execution (2026-10-30)

## Implemented and tested in this release
- [x] Advisory edge alignment hints with shift vectors; **no** warping or silent registration (`scripts/advanced_visual_qa.py`).
- [x] Component tolerances by semantic priority, with clipping as an unconditional rejection (`scripts/validate_component_geometry.py`).
- [x] Local licensed-font name/weight metadata comparisons; effective browser CSS, line wrapping and font availability probes (`scripts/audit_typography_icons.py`, `scripts/browser_font_audit.py`). **Same-metric fallback remains fundamentally inconclusive without source fonts.**
- [x] Mask-aware region scores and SSIM, an 8% hard total mask ceiling and protection for critical regions (`scripts/advanced_visual_qa.py`).
- [x] Original/restored SVG icon raster comparisons: shape IoU, baseline, fill and stroke weight proxy (`scripts/audit_typography_icons.py`).
- [x] Android-style Chromium mobile tap/keyboard focus and a native Chromium touch swipe sequence on a fixture (`scripts/browser_compat_qa.py`). Browser engine is Chromium on Linux, **not an actual Android device**.
- [x] Component-by-component reviewer-only CSS delta proposals, without applying changes (`scripts/advanced_visual_qa.py`).
- [x] Machine-readable and Markdown state dashboards with image links (`scripts/build_state_dashboard.py`).
- [x] Interactive, entirely local split overlay inspector with original bytes unchanged (`scripts/advanced_visual_qa.py`).
- [x] Safe CI artifact definition for metrics and error logs; proprietary screenshots excluded unless explicitly authorized. Historical GitHub runs retain artifacts with bounded retention, but an automatic multi-run aggregator is still open.
- [x] Agent CLI inventory and native install-path probe. Missing clients are reported as **NOT TESTED**, not compatible-by-test (`scripts/probe_agents.py`).
- [x] Synthetic negative-control harness that executes four rejection cases and measures false positives (`scripts/negative_controls.py`).

## Still blocked / independently verifiable TODOs
- [ ] **P0:** Benchmark three independent real projects with owner-approved **non-derived** references at mobile, tablet and desktop. Present material has Catty (mobile), iFood PiP (desktop), and synthetic fixtures. Missing references prevent this acceptance gate. The coverage checker rejects these fixtures correctly.
- [ ] **P0:** Verify a completely autonomous run by a connected image-capable code agent: input image -> layer assets -> implementation -> real browser -> correction loop -> output. Tool QA is not a substitute for agent-driven execution. Requires an actual connected agent runtime and its permissions.
- [ ] **P0:** Recover high-resolution original isolated Catty source layers, if they exist. Current approved visual is flattened; hidden paws cannot be reconstructed exactly from screenshots. **Do not generate speculative layers and claim them as originals.**
- [ ] **P1:** Exercise actual Claude Code, Codex, OpenCode, Hermes, Codebuff/Freebuff, Cursor and Gemini CLI installations with credentials in their native environments. The sandbox has no such executables. Layout/installer tests alone are insufficient.
- [ ] **P1:** Perform real iOS Safari/WebKit and Android device touch/gesture, safe-area, focus and voiceover testing. Chromium fixture test passed; WebKit executable is unavailable and real mobile hardware is not present.
- [ ] **P1:** Confirm typeface identity with licensed original font bytes and a platform-appropriate font raster test. Generic CSS font names/line wraps cannot prove the precise face when original font is unavailable.
- [ ] **P2:** Aggregate historical CI metrics across workflow runs automatically into a longitudinal dashboard. Per-run logs and artifact retention now exist, but cross-run ingestion requires GitHub Actions artifact read permissions or a user-provided baseline.

## Evidence integrity
- SSIM/MAE/icon IoU are diagnostic; do not map directly to a 0–10 quality rating.
- A synthetic zero false-positive rate does not establish field false-positive rate.
- Browser geometry cannot approve a cropped phone, missing paw or overwritten source lighting.
- Never publish private reference screenshots or licensed fonts from this test data to the public repository.
## v1.8.0 — Environment readiness and remaining acceptance gates

- [x] Prepare isolated native directories and optional official npm installation probes for Claude Code, Codex, OpenCode, Codebuff/Freebuff and Gemini CLI. Hermes/Cursor installers are left for explicit manual review.
- [x] Add authoritative font file identity checker with SHA-256, metadata and a fail-closed missing-source status.
- [x] Add automatic post-CI/weekly longitudinal aggregation and per-run sanitized QA artifact emission, with unavailable older data marked N/D.
- [ ] Run each external CLI with provider authorization on a real image-to-code case, collect an actual browser screenshot and correction trace. Installation checks alone do not satisfy this.
- [ ] Provide approved licensed font files (or verified hashes) for Catty and other benchmarks; until then exact font identity is unconfirmed.
- [x] Gather three successive CI executions with usable QA metric artifacts (3/3 observed, 80 Python + 5 JavaScript + 4 browser gates per run). This is early trend coverage only; 21 older runs lack these artifacts.
- [ ] Review native Hermes/Cursor installers and execute them on a supported, isolated environment; do not pipe unreviewed remote scripts into a shell.

## Evidências de preparação v1.8.0

- [x] Six npm code-agent CLIs installed and returned version numbers on isolated CI runners: Claude Code 2.1.314, Codex 0.166.0, OpenCode 2.2.4, Freebuff 0.2.35, Codebuff 1.0.688, Gemini CLI 0.66.0. Evidence: [workflow 41099774039](https://github.com/lenixeduardo/Image-to-code/actions/runs/41099774039). Installation and `--version` are **not** authenticated skill invocation.
- [x] CI history collector recovered metrics from three successive successful runs; 21 older records correctly report missing historical artifacts. Evidence: [workflow 41099885256](https://github.com/lenixeduardo/Image-to-code/actions/runs/41099885256).
- [ ] Hermes and Cursor CLI official installer review/execution on isolated hosts; still not verified.
- [ ] Exact Catty typeface identity: repository CSS declares DM Sans and Pacifico but has no bundled original font files, and screenshots do not contain source font bytes. Obtain approved original font files or hash.
