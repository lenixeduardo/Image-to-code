# Technical audit — Image to Code v1.1.0

This file documents what has and has not been verified. It is not a claim that every screenshot can be reconstructed perfectly.

## Confirmed tests

- 14 Python tests: crop extraction, palette inventory, JSON schema validation, region bounds, unsafe paths, flood-fill edge cases, mask integrity, visual mismatch guard, presentation boards, strict desktop viewport gate, and synthetic pipeline.
- 3 Node.js tests: viewport CLI parsing, malformed input validation, and browser check decision logic.
- `node --check scripts/capture.mjs` and `python -m compileall -q scripts`.
- Real historic iFood PiP screenshot replay from preexisting captures: source 1179×642 included external bars, explicitly cropped to XYWH (0,16,1179,616) for comparison to a 1179×616 rendered screenshot. The diagnostic threshold mismatch fraction was 0.206989 (20.7%), not a fidelity rating.
- In-chat demonstration boards are created using preserved, **preexisting screenshots**, not newly captured browser pages.

## Limitations and incomplete checks

- End-to-end browser automation **was not executed in the current restricted environment**: the Chromium binary runs but navigation is blocked by administrator policy, and the Node Playwright package cannot be installed from the inaccessible npm registry. The capture engine's browser-specific path requires validation in an unrestricted CI/local browser.
- No independent reference screenshots exist for mobile/tablet, so their visual fidelity is inferred, not measured.
- Font identification and hidden or occluded asset recovery cannot be guaranteed from arbitrary screenshots.
- No proof of pixel-perfect fidelity across arbitrary websites; the scripts are tools supporting an agent workflow, not a vision model.

## Release v1.1.0 changes

1. Browser capture now detects broken images, runtime exceptions, accessible-name gaps, absent main landmarks, horizontal overflow, failed requests, and accepts reference-matched viewport and smoke widths.
2. Diff masks now affect all output diagnostic images and metrics, with excluded pixels clearly identified.
3. Component bounds, asset-path safety and invalid crop tolerance validation were hardened.
4. `--require-matching-desktop` makes incorrect desktop comparisons fail acceptance rather than merely warn.
5. CI now syntax-checks JavaScript and runs dependency-free Node tests alongside expanded Python tests.
6. Documentation corrects the GitHub clone path and distinguishes tooling tests from browser-based QA.

**Interpretation:** 17 passing automated tests support the reliability of the deterministic tools. They do not independently establish a 10/10 visual fidelity score for reconstructed interfaces.

## v1.4.0 — New regression protocol (2026-10-30)

- User-reported Catty analysis-2 issues are tracked as one unique regression set (the two requests repeated the same defects): icons differ; typography differs slightly; CTA too large; illustrated subject has baked-in glow; replacement introduces upper/lower blur and loses paw.
- Two independent review scopes plus one acceptance scope are specified in `references/fidelity-gates.md`. This skill repository has no autonomous agent runtime; role definitions do not prove three subagents actually ran.
- Added strict region and immutable SHA-256 asset checks to `scripts/audit_fidelity_contract.py` with synthetic positive/negative tests. Oversized button geometry is rejected without scaling its crop; substituted icon/font pixel shapes, changed assets, missing glow/paw regions, invalid references and incomplete required categories are rejected.
- The real approved Catty mockup/source composite and a browser capture were **not supplied to this skill repository audit**. No real Catty render comparison or Catty-site 9.5/10 fidelity score is claimed here. Application corrections require a separate change to the Catty application repository.
- The standalone regression tests verify gate behavior on synthetic fixtures, not the fidelity of the actual Catty page.

## v1.3.0 — Catty full-stack regression case

Tested against `lenixeduardo/catty-minhaamiga` with approved three-screen mobile mockup and a GitHub Actions Chromium run. The separate Catty QA branch/PR reported 25/31 checks passing, with five missing image variants and one desktop tab interaction failing. Original Catty application tests: 36 passed, 4 failed, 2 skipped. Build passed. Gemini Live streaming and authenticated Supabase were not validated without real secrets/device permissions.

New `scripts/audit_project_assets.py` scans static quoted paths in source and tests whether corresponding public assets exist, even when browser fallback images are loaded successfully. It identified all five missing Catty assets. This is a necessary quality gate, not proof that a coding agent can generate arbitrary UIs from scratch. Full end-to-end image-to-code score remains non-perfect until reference assets and interactive behavior are validated.

## v1.4.0 — Multi-agent installation (October 2026)

- New Python stdlib installer: `scripts/install.py`, with project/global paths for Claude Code, Freebuff/Codebuff, OpenCode, Hermes, Codex, Cursor, Gemini CLI, and an open-standard generic route.
- Explicit `--dry-run`, `--verify` (SHA-256), backup-preserving `--force`, shared `.agents/skills` deduplication, and symlink rejection.
- Agent-compatibility reference documents verified directories and platform-specific trust requirements.
- Automated tests verify path mapping, real copies of fixtures, idempotence protection, updates with backups, tamper detection, dry-run, shared target deduplication, symlink rejection, and missing-project protection.
- **Scope of proof:** installer and Python/Node helpers can be tested automatically. This is *not* proof that each external model or remote agent produced pixel-perfect code; full target-agent runs require separate tests and image-capable models.

## v1.4.0 — Multi-agent distribution + independent visual QA

- Added dependency-free, cross-platform `scripts/install.py` and `tests/test_install.py`. The installer supports Claude Code, OpenCode, Freebuff/Codebuff, Hermes, Codex, Cursor, Gemini CLI and generic Agent Skills compatible directories, project or global scope, SHA-256 verification, backup-based upgrades, symlink guards, and dry-run. It copies one canonical bundle; native execution by these agent CLIs **has not been claimed**.
- Documented discovery and trust requirements in `references/agent-compatibility.md`, including Hermes workspace trust. Official sources in that file.
- Added `references/visual-review-agents.md`, `scripts/validate_visual_review.py`, and synthetic failure/success tests in `tests/test_visual_review.py`. Four independent review categories prevent a successful browser smoke test from masquerading as visual fidelity.
- Catty mobile at 390×844 was audited locally against its approved 390×844 normalized mockup. Painted CTA area: reference approx. 346×44 px; reconstruction 342×45 px (the latter is 4 px narrower and 1 px taller). Icons, typography, clipped paw, and added blurred lighting remain **not approved**. The image extraction used in the previous local preview contains unwanted remnants from the original screenshot; it must not be labeled a recovered original asset.
- The Catty example and its private reference images are **not included** in the public skill repository. No changes to Catty's GitHub repository are part of this release.
- Local tests: `python -m unittest discover -s tests -p 'test_*.py' -q` (32 passing) and `node --test tests/test_capture.mjs` (3 passing). GitHub CI must separately confirm after publication.

## v1.5.0 — Video-demonstrated image regeneration workflow

- The user's 19-second recording demonstrates **reference screenshot → forensic scene prompt → regenerate a complete clean scene (no text) → add text faithfully as a second pass**. The crop is a conditioning input and never the final asset.
- Added `references/reference-guided-regeneration.md`, a Catty-specific scene-only prompt template, `scripts/prepare_generation_reference.py`, and `scripts/validate_generation_cycle.py` with negative tests for copied crops, missing reference images, lost paws, duplicate CSS glow, lack of typographic checks, untracked generations, and path traversal.
- Full skill local verification: **45 Python tests** and **3 Node tests** passed.
- This validates the deterministic controls and instructions **not** an external generator's actual adherence to a visual reference. No generator is bundled; real visual fidelity requires an image-capable agent and visual comparison. The Catty repository was not modified.

## v1.6.0 — Multi-state pixel-perfect regression gates (Catty validation)

- Added deterministic per-screen reference-vs-browser calibration including pair images, heatmaps, MAE, mismatch fraction and optional SSIM, with an explicit reference-normalization control and baseline comparison.
- Added browser visibility/geometry checks that reject clipped required elements, overflow and missing images even when dialogue text and navigation tests pass; CI positive and negative fixture cases.
- New `TODO.md` separates completed infrastructure from unverified agent performance, font matching, source-layer recovery and visual benchmarks.
- Source screenshots for Catty remain outside the public repository. These tooling checks are **not** proof of automatic 9.5/10 reconstruction quality.


## v1.7.0 — Advanced QA / backlog execution

- Added read-only region and mask-aware perceptual analysis, advisory alignment, strict semantic component geometry thresholds, source-based SVG/font audits and browser font/wrap checks.
- Added Chromium native-touch/focus fixture, WebKit availability reporting, agent CLI discovery without false runtime claims, executed negative controls, benchmark-reference coverage checker, reviewer-only CSS suggestions and local state dashboards.
- Catty's three approved mobile states rendered in a browser and compared with local reference panels; screenshots, proprietary images and fonts were **not committed**. Local scores are diagnostic and do not prove universal fidelity.
- The three-independent-project P0 benchmark, autonomous external coding-agent run, original Catty source layers, real external CLIs and physical Safari/Android device tests remain open pending external materials and execution environments. See TODO.md.


## v1.8.0 — CLI environments, font provenance and CI trends

- Prepared native skill directories for eight code agents and an opt-in isolated official npm CLI installation workflow (manual dispatch). Local execution did not find installed CLI binaries or provider credentials; model invocations remain NOT_AUTHENTICATED.
- Added FontTools source-byte SHA-256 checks with an explicit ORIGINAL_UNAVAILABLE result, plus metadata. The approved Catty source font was not available, so definitive identity is not claimed.
- Added CI job metric emission and an independent `workflow_run`/scheduled historical aggregator using read-only GitHub Actions API access. Exports JSON, CSV, MD and HTML without proprietary screenshots, tokens or font files. Old missing/expired artifacts produce N/D.
- Unit tests cover missing/identical/different font bytes, CLI placement and historical-metrics integrity; a successful CLI version check is not autonomous image-to-code execution.

## v1.8.0 — Real runner evidence (2026-10-30)

- [CLI smoke matrix](https://github.com/lenixeduardo/Image-to-code/actions/runs/41099774039): all six npm CLI runners completed with executable version checks; **no agent auth, no autonomous image-to-code invocation**. Versions: Claude Code 2.1.314, Codex 0.166.0, OpenCode 2.2.4, Freebuff 0.2.35, Codebuff 1.0.688, Gemini CLI 0.66.0.
- [Historical metrics aggregation](https://github.com/lenixeduardo/Image-to-code/actions/runs/41099885256): recovered 3 fully measured runs with 80/80 Python, 5/5 JavaScript and 4/4 browser gates each. 21 older runs have no compatible metrics artifact. Initial API download produced a false missing-data result; repaired with GitHub CLI fallback and verified the archive contents.
- Font check reports `ORIGINAL_UNAVAILABLE` for approved Catty font source. Declared CSS families DM Sans and Pacifico were observed in the original repository, not proven identical to flattened mockup typography. No fonts were uploaded.
