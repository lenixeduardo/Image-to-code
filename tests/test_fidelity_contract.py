"""Fidelity regression scenarios based on reported Catty analysis-2 defects."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/audit_fidelity_contract.py'


class FidelityContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.ref = self.root / 'reference.png'
        self.render = self.root / 'render.png'
        im = Image.new('RGB', (240, 180), '#1a111a')
        dr = ImageDraw.Draw(im)
        dr.rectangle((12, 10, 31, 29), fill='#ffffff')  # icon
        dr.rectangle((10, 40, 160, 62), fill='#eeeeee')  # font/glyph envelope
        dr.rounded_rectangle((15, 75, 155, 112), radius=18, fill='#ffffff')  # CTA
        dr.ellipse((90, 116, 166, 175), fill='#ff8ebc')  # composite/glow
        dr.rectangle((108, 164, 128, 175), fill='#fff9ee')  # paw detail
        im.save(self.ref)
        im.save(self.render)
        asset = self.root / 'public' / 'catty.webp'
        asset.parent.mkdir(parents=True)
        asset.write_bytes(b'approved exact artwork with baked in lights')
        self.asset = asset
        self.contract = {
            'version': 1, 'reference': 'reference.png', 'render': 'render.png',
            'required_categories': ['icon', 'typography', 'button', 'artwork'],
            'require_protected_assets': True,
            'regions': [
                self.region('feature-icon', 'icon', [10, 8, 25, 25]),
                self.region('headline', 'typography', [8, 38, 156, 27]),
                self.region('cta', 'button', [15, 75, 141, 38]),
                self.region('catty-glow-and-paw', 'artwork', [85, 115, 90, 65])
            ],
            'protected_assets': [{'id': 'hero', 'path': 'public/catty.webp', 'sha256': hashlib.sha256(asset.read_bytes()).hexdigest()}]
        }

    @staticmethod
    def region(ident, category, box):
        return {'id': ident, 'category': category, 'reference_bounds': box, 'render_bounds': box,
                'max_position_delta_px': 0, 'max_size_delta_px': 0,
                'pixel_tolerance': 10, 'max_mismatch_fraction': 0.02}

    def run_audit(self, expected=0):
        path = self.root / 'contract.json'
        path.write_text(json.dumps(self.contract))
        result = subprocess.run([sys.executable, str(SCRIPT), '--contract', str(path), '--project', str(self.root), '--out', str(self.root / 'report.json')], capture_output=True, text=True)
        self.assertEqual(result.returncode, expected, result.stderr + result.stdout)
        return json.loads((self.root / 'report.json').read_text()) if expected in (0, 1) else result

    def test_identical_reference_and_original_asset_pass(self):
        report = self.run_audit()
        self.assertTrue(report['passed'])
        self.assertTrue(all(r['passed'] for r in report['regions']))

    def test_oversized_cta_fails_without_resampling(self):
        self.contract['regions'][2]['render_bounds'] = [15, 75, 175, 38]
        report = self.run_audit(expected=1)
        self.assertFalse(report['regions'][2]['geometry_ok'])
        self.assertIsNone(report['regions'][2]['mismatch_fraction'])

    def test_replaced_icon_and_font_shape_are_caught(self):
        im = Image.open(self.ref)
        dr = ImageDraw.Draw(im)
        dr.rectangle((12, 10, 31, 29), fill='#ff1685')
        dr.rectangle((10, 40, 160, 62), fill='#9a9a9a')
        im.save(self.render)
        report = self.run_audit(expected=1)
        self.assertEqual([r['category'] for r in report['regions'] if not r['passed']], ['icon', 'typography'])

    def test_missing_paw_and_blurred_glow_detected(self):
        im = Image.open(self.ref)
        dr = ImageDraw.Draw(im)
        dr.rectangle((105, 155, 140, 179), fill='#ff8ebc')
        dr.ellipse((90, 116, 166, 175), outline='#b92b86', width=6)
        im.save(self.render)
        report = self.run_audit(expected=1)
        self.assertEqual([r['id'] for r in report['regions'] if not r['passed']], ['catty-glow-and-paw'])

    def test_original_asset_altered_even_with_identical_render(self):
        self.asset.write_bytes(b'regenerated lookalike')
        report = self.run_audit(expected=1)
        self.assertFalse(report['protected_assets'][0]['passed'])

    def test_rejects_viewport_mismatch(self):
        Image.new('RGB', (200, 180)).save(self.render)
        self.run_audit(expected=2)

    def test_rejects_missing_artwork_region(self):
        self.contract['regions'] = self.contract['regions'][:-1]
        report = self.run_audit(expected=1)
        self.assertTrue(any('required category artwork' in x for x in report['failures']))

    def test_rejects_escape_from_project(self):
        self.contract['protected_assets'][0]['path'] = '../other-image.png'
        self.run_audit(expected=2)

    def test_rejects_unprotected_composite(self):
        self.contract['protected_assets'] = []
        report = self.run_audit(expected=1)
        self.assertTrue(any('protected source assets required' in x for x in report['failures']))


if __name__ == '__main__':
    unittest.main()
