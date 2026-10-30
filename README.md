# Image to Code — Layer First

<picture>
  <source media="(max-width: 640px)" srcset="assets/cover-mobile.png">
  <img src="assets/cover.png" alt="Image to Code — Layer First: comparação real entre captura original e reconstrução, com crédito a Lenix Eduardo" width="1920">
</picture>

**Created by Lenix Eduardo Rotundo de Camargo** · GitHub: [@lenixeduardo](https://github.com/lenixeduardo) · License: MIT

[Leia em português (Brasil)](README.pt-BR.md)

## Reference-guided scene regeneration (v1.5.0 — video workflow)

For explicit recreation requests, **the screenshot crop is a reference image passed to the generator, not the final asset**. The agent examines the original screenshot and crop, writes a visually grounded detailed prompt, generates the **full cohesive scene without texts**, visually reviews identity/paws/glow, then adds the exact original typography **in a second pass**. On web pages, titles and CTAs are real HTML/CSS. On requested static posters, the second pass may be a text-overlay image edit. No duplicate CSS glow over a scene that already includes its highlights.

1. `python scripts/prepare_generation_reference.py reference.png --box X Y W H --out artifacts/reference/component.png --manifest artifacts/reference/crop.json`
2. Read [`references/reference-guided-regeneration.md`](references/reference-guided-regeneration.md) and author `artifacts/regeneration/scene-prompt.md`.
3. Give **both images + prompt** to an image-capable agent, review each generation and keep the text-free scene master.
4. Restore typography and interactions separately; validate the [`generation contract`](scripts/validate_generation_cycle.py) and screenshot comparisons.

[Catty scene-only prompt example](examples/catty-hero-scene-prompt.md). **A detailed prompt cannot guarantee 100% identical output**; the mandatory acceptance reviews catch mismatched identity, added bows/hair/phones, clipped paws and baked duplicate glows. If the agent has no image generator, it must report the blocker rather than relabel a screenshot crop as regenerated art.


A reusable **Agent Skill** for converting screenshots and mockups into working, responsive user interfaces. It starts by mapping **background → layout → components → typography → icons → images → fine details**, then builds the page and audits the rendered result.

**Scope:** A skill defines an agent workflow, not a standalone computer-vision or image-generation model. Scripts assist with deterministic crops, schema validation, browser captures and visual QA.

## Install for any coding agent

One canonical [Agent Skills](https://agentskills.io/) bundle works with **Claude Code, OpenCode, Freebuff/Codebuff, Hermes, Codex, Cursor, Gemini CLI**, and other compatible code agents. The installer uses only Python 3.10+ standard library; it preserves existing installations unless `--force` is explicitly supplied.

```bash
git clone https://github.com/lenixeduardo/image-to-code.git
cd image-to-code
python scripts/install.py --agent all --scope project --project /path/to/your-app
# Alternatively install per-user for selected agents:
python scripts/install.py --agent claude,opencode,freebuff,hermes --scope global
# Verify or back up before replacing:
python scripts/install.py --agent all --scope project --project /path/to/your-app --verify
python scripts/install.py --agent all --scope project --project /path/to/your-app --force
```

The agent-specific directories are `.claude/skills/`, `.opencode/skills/`, `.agents/skills/` (Freebuff and Codex), `.hermes/skills/`, `.cursor/skills/`, and `.gemini/skills/`. **Hermes project skills need `hermes skills trust`.** Windows: use `py -3` if needed. See the [compatibility matrix and installation reference](references/agent-compatibility.md) for global paths and verified source links. Native detection does **not** guarantee image understanding, browser access, or fidelity until tested in the chosen agent.


## New: Catty regression protection and three review agents (v1.4.0)

The skill now requires a **UI fidelity reviewer** (icons, loaded fonts and CTA geometry), an **asset forensics reviewer** (approved originals, baked-in glows, blur artifacts, visible paws), and an **independent acceptance reviewer**. Use real subagents when the host supports them; otherwise keep separate manual review reports and disclose the limitation.

`scripts/audit_fidelity_contract.py` fails independently on regions with wrong pixel content or geometry, missing required region categories and changed/missing protected original assets. Use `examples/catty-analysis-2.contract.example.json` as a schema-shaped starting point, **not** as real Catty measurements. Replace all example coordinates and hashes with verified evidence. See [the strict review protocol](references/fidelity-gates.md). These are regression checks for the skill; they do not claim the Catty website itself is fixed or that real visual fidelity has been proven.

## What it produces

- Layer map with positions, dimensions, opacity/stacking strategy and provenance.
- Asset manifest (original / cropped / CSS rebuilt / missing), with file names and legal source status.
- Design spec in JSON: colors, gradients, typography, headings, body text, components, spacing, responsive rules and evidence confidence.
- Implemented frontend in the **target project's existing framework**.
- Captures of mobile (390×844), tablet (820×1180) and desktop (1440×900); audit report and reference comparisons when screenshots exist at matching sizes.
- **Mandatory inline chat presentation:** mobile + tablet side-by-side; if the reference is a desktop UI screenshot, original desktop + rebuilt desktop side-by-side. Never replace these with links only.
- An honest manual fidelity score where a reference exists; goal ≥9.5/10, **not** an automated claim based solely on pixel similarity.

## Compatibility and invocation

Claude Code: `/image-to-code`; Codex: `$image-to-code`; Freebuff/Codebuff: `/skill:image-to-code`; Hermes: `/image-to-code`; Cursor: `/image-to-code` (or `@image-to-code`). For OpenCode and Gemini CLI, request that the agent load the `image-to-code` skill using their native skill-discovery interface. Platform CLI commands and permissions may vary by version; see [verified agent documentation](references/agent-compatibility.md).

If the agent cannot read images or run a local browser, it can still inspect the repository and produce a documented partial result, but it must **not** report screenshot fidelity as verified. The installer does not deploy applications, change providers or automatically invoke the agent.

## Example agent request

> Use `$image-to-code` to recreate the attached mockup in my current Next.js project. First break it down into background, grids, components, font families, title/body sizes, icons and images. Export assets separately when technically recoverable. Document desktop/tablet/mobile behavior and implement the page. Capture all three viewports, compare visually and correct the differences. Preserve the original artwork and report anything inferred or not recoverable.

## Quality controls — v1.1.0

- The screenshot helper checks for missing images, JavaScript errors, unnamed interactive controls, missing page landmarks, and horizontal overflow. It fails on these errors by default.
- Browser capture supports a reference-matched viewport and additional widths: `node scripts/capture.mjs --url http://localhost:3000 --reference-viewport 1179x616 --smoke-widths 360,430,768,1024,1280,1920`. `--allow-warnings` is only for diagnostics, **not** acceptance.
- For acceptance, add `--require-matching-desktop` to `present_results.py` to fail when comparison dimensions differ.
- Pixel diff masks affect **both metrics and exported evidence**, including `threshold-diff.png`; excluded regions are marked in gray in the overlay and original image differences are never hidden silently.
- Run `python -m unittest discover -s tests -v` and `node --test tests/test_capture.mjs` before accepting a result. A successful test run verifies the scripts but **does not prove pixel-perfect reconstruction** without a browser and user reference images.
- If the environment blocks navigation or lacks a browser, record the blocker instead of inventing screenshots or saying the end-to-end test passed.

## Optional scripts

Install deterministic helpers:

```bash
python -m pip install -r requirements.txt
```

Measure screenshot dimensions and candidate palette:

```bash
python scripts/image_inventory.py input/reference.png --out artifacts/inventory.json
```

Replace sample coordinates with actual measured rectangles (pixel XYWH):

```bash
python scripts/export_layers.py input/reference.png --regions examples/regions.example.json --out artifacts/assets
```

Validate a filled-in design spec:

```bash
python scripts/validate_spec.py artifacts/design-spec.json
```

Browser screenshot automation (optional, requires a **running local page**):

```bash
npm install
npx playwright install chromium
node scripts/capture.mjs --url http://localhost:3000 --out artifacts/screenshots
```

Generate standardized presentation boards:

```bash
python scripts/present_results.py \
  --mobile artifacts/screenshots/mobile.png \
  --tablet artifacts/screenshots/tablet.png \
  --desktop artifacts/screenshots/desktop.png \
  --reference input/desktop-reference.png \
  --desktop-reference-render artifacts/screenshots/desktop-matching-reference.png \
  --reference-kind desktop --out artifacts/presentation
```

Produces `mobile-tablet-side-by-side.png` and `desktop-original-vs-render.png`, plus a manifest. The images must be displayed **directly in the chat**; downloadable files are supplementary. With a mobile/tablet input, it produces `desktop-preview.png` instead of inventing a desktop original. A viewport mismatch is flagged on the board and cannot substantiate a visual fidelity score. See [presentation standard](references/presentation-standard.md).

Compare an original and a render with the **same dimensions**, without rescaling:

```bash
python scripts/audit_visual.py --reference input/reference.png --render artifacts/screenshots/desktop.png --out artifacts/audit/desktop
```

Three files appear: `overlay.png`, `diff.png`, `threshold-diff.png`, plus `report.json`. Pixel metrics diagnose differences; they are not visual quality scores.

## Repository layout

```text
image-to-code/
├── SKILL.md                         # Main agent instructions
├── agents/openai.yaml               # Optional host UI metadata
├── references/
│   ├── layer-analysis.md            # Back-to-front reconstruction
│   ├── design-spec.schema.json       # Machine-validatable spec
│   ├── spec-guide.md                # Data model and evidence rules
│   ├── responsive-rules.md          # Mobile / tablet / desktop
│   ├── implementation-guide.md      # DOM/CSS implementation
│   ├── visual-qa.md                 # QA and score rubric
│   └── presentation-standard.md     # Mandatory paired visual demonstrations
├── scripts/
│   ├── image_inventory.py
│   ├── export_layers.py
│   ├── validate_spec.py
│   ├── audit_visual.py
│   ├── capture.mjs
│   └── present_results.py          # Paired mobile/tablet and desktop boards
├── examples/                       # Synthetic examples only
├── tests/                          # Regression checks
├── requirements.txt
├── package.json
└── .github/workflows/ci.yml
```

## Boundaries

1. One screenshot proves only that viewport. Mobile/tablet adaptations are inferences until additional references exist.
2. Exact font identification and invisible image pixels cannot be guaranteed from a screenshot.
3. Screenshot fragments are not magically isolated design assets; background removal is safe only for sufficiently simple flat regions and always needs inspection.
4. Text must remain selectable and accessible, not simply cropped to images.
5. Do not generate/recreate protected logos or replace supplied artwork without authorization. Respect licenses on fonts, icons, photos and source images.
6. A script cannot generate missing art on its own; a supported asset-generation or image-editing tool is required for those steps.

## Run local checks

```bash
python -m unittest discover -s tests -v
python scripts/validate_spec.py examples/design-spec.example.json
```

## Publishing to GitHub

After creating a new empty repository on GitHub:

```bash
git init
git add .
git commit -m "feat: add layer-first image-to-code agent skill"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/image-to-code-skill.git
git push -u origin main
```

The repository is compatible with the open Agent Skills `SKILL.md` layout: [agentskills.io](https://agentskills.io/specification). OpenAI also documents this convention in [Build skills](https://learn.chatgpt.com/docs/build-skills).

## Credits and authorship

- **Creator / author:** Lenix Eduardo Rotundo de Camargo ([@lenixeduardo](https://github.com/lenixeduardo)).
- Source project: Image to Code — Layer First.
- See [AUTHORS.md](AUTHORS.md) and [LICENSE](LICENSE) for attribution and licensing.

## License

MIT for the code and instructions in this repository. It does not confer rights to third-party source images, fonts, trademarks or assets.

## Asset consistency for existing websites / Integridade de assets

Run `python scripts/audit_project_assets.py --project /path/to/project --out artifacts/project-assets.json` to detect references to missing images before and after generation. A fallback image rendering successfully does **not** establish that the original asset was recovered. Dynamic imports or remote assets require manual inspection.


## Visual fidelity review gate

The four independent review categories (icons, typography/controls, character anatomy, baked-in lighting/composition) are documented in [`references/visual-review-agents.md`](references/visual-review-agents.md). Before claiming a pixel-fidelity score, provide real visual evidence and validate `artifacts/visual-review.json` with `python scripts/validate_visual_review.py --file artifacts/visual-review.json --root .`. Browser smoke checks alone never prove pixel accuracy.
