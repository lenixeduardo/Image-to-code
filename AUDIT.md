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

## Functional audit update — v1.2.0

- CI now launches actual Chromium on GitHub Actions and captures a responsive fixture; a separate fixture intentionally contains a broken image and **must** fail.
- The browser report checker validates mobile/tablet/desktop/reference-width and smoke viewports, HTTP status, images, console errors, accessible controls, main landmark, and horizontal overflow.
- The local tool environment still blocks browser navigation (`ERR_BLOCKED_BY_ADMINISTRATOR`). The new GitHub CI job is the authoritative environment for the browser runner.
- This is a real browser **capture-engine integration test**, not a demonstration that an AI agent can infer and implement arbitrary pages without human or model involvement. The skill's semantic layer analysis and code authoring depend on an image-capable coding agent.


## Live GitHub CI verification — v1.2.0

- Run: https://github.com/lenixeduardo/Image-to-code/actions/runs/40992671341
- Head commit: `41a6762cbba44b5a4f6839317b63bc8001b86243`.
- `tests`: **success** (14 Python tests and 3 Node unit tests).
- `browser-integration`: **success**, exercising actual Playwright Chromium for valid and deliberately broken responsive fixture pages.
- The integration run checks screenshot output, reference viewport, accessible names, broken images, console errors, failed requests and horizontal overflow.
- Scope: these results verify the functional supporting tools, **not** autonomous semantic image interpretation or universal screenshot-to-code fidelity; implementation still requires an image-capable coding agent.
