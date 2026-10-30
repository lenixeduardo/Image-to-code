# Image to Code — Layer First

<picture>
  <source media="(max-width: 640px)" srcset="assets/cover-mobile.png">
  <img src="assets/cover.png" alt="Image to Code — Layer First: comparação real entre captura original e reconstrução, com crédito a Lenix Eduardo" width="1920">
</picture>

**Created by Lenix Eduardo Rotundo de Camargo** · GitHub: [@lenixeduardo](https://github.com/lenixeduardo) · License: MIT

[Leia em português (Brasil)](README.pt-BR.md)

A reusable **Agent Skill** for converting screenshots and mockups into working, responsive user interfaces. It starts by mapping **background → layout → components → typography → icons → images → fine details**, then builds the page and audits the actual rendered result.

**Scope:** a skill defines the agent workflow; it is not a standalone AI model that automatically recognizes every font, retrieves images hidden behind cards, or implements a webpage without an image-capable coding agent. The included deterministic scripts support image inspection, selected asset crops, schema validation, browser captures, and pixel-difference evidence.

## What it produces

- Layer map with positions, dimensions, opacity/stacking strategy and provenance.
- Asset manifest (original / cropped / CSS rebuilt / missing), with file names and legal source status.
- Design spec in JSON: colors, gradients, typography, headings, body text, components, spacing, responsive rules and evidence confidence.
- Implemented frontend in the **target project's existing framework**.
- Captures of mobile (390×844), tablet (820×1180) and desktop (1440×900); audit report and reference comparisons when screenshots exist at matching sizes.
- **Mandatory inline chat presentation:** mobile + tablet side-by-side; if the reference is a desktop UI screenshot, original desktop + rebuilt desktop side-by-side. Never replace these with links only.
- An honest manual fidelity score where a reference exists; goal ≥9.5/10, **not** an automated claim based solely on pixel similarity.

## Install in Codex or a compatible Agent Skills runner

As a globally discoverable skill:

```bash
git clone https://github.com/lenixeduardo/Image-to-code.git image-to-code
mkdir -p ~/.agents/skills
cp -R image-to-code ~/.agents/skills/image-to-code
```

For one project, copy into the repository:

```bash
mkdir -p .agents/skills/image-to-code
cp -R /path/to/image-to-code/{SKILL.md,agents,references,scripts,examples,requirements.txt} .agents/skills/image-to-code/
```

The host needs to support loading Agent Skills and have access to your visual reference and target code repository. In Codex, invoke `$image-to-code` or select it from skills; in other compatible hosts, use their invocation method.

## Example agent request

> Use `$image-to-code` to recreate the attached mockup in my current Next.js project. First break it down into background, grids, components, font families, title/body sizes, icons and images. Export assets separately when technically recoverable. Document desktop/tablet/mobile behavior and implement the page. Capture all three viewports, compare visually and correct the differences. Preserve the original artwork and report anything inferred or not recoverable.

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
git remote add origin https://github.com/lenixeduardo/Image-to-code.git
git push -u origin main
```

The repository is compatible with the open Agent Skills `SKILL.md` layout: [agentskills.io](https://agentskills.io/specification). OpenAI also documents this convention in [Build skills](https://learn.chatgpt.com/docs/build-skills).

## Credits and authorship

- **Creator / author:** Lenix Eduardo Rotundo de Camargo ([@lenixeduardo](https://github.com/lenixeduardo)).
- Source project: Image to Code — Layer First.
- See [AUTHORS.md](AUTHORS.md) and [LICENSE](LICENSE) for attribution and licensing.

## License

MIT for the code and instructions in this repository. It does not confer rights to third-party source images, fonts, trademarks or assets.


### Functional QA / CI browser test

The GitHub workflow runs a real Playwright Chromium integration test with a valid responsive page and a deliberately broken image case. The capture engine must accept the first and reject the second. These checks validate the **skill tooling**, not automatic image understanding or fidelity to unseen references.
