"""Synthetic-data integration tests; no claims of UI reconstruction."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


class ToolTests(unittest.TestCase):
    def test_image_inventory_and_crop(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            img = Image.new('RGB', (80, 60), '#ffffff')
            for x in range(20, 40):
                for y in range(10, 30):
                    img.putpixel((x, y), (20, 60, 150))
            source = root / 'reference.png'
            img.save(source)
            inventory_out = root / 'inventory.json'
            subprocess.run([sys.executable, str(ROOT / 'scripts/image_inventory.py'), str(source), '--out', str(inventory_out)], check=True, capture_output=True)
            inventory = json.loads(inventory_out.read_text())
            self.assertEqual((inventory['width_px'], inventory['height_px']), (80, 60))
            regions = root / 'regions.json'
            regions.write_text(json.dumps({'regions': [{'id': 'blue-block', 'kind': 'icon', 'bounds': [15, 5, 30, 30], 'remove_border_background': True}]}))
            out = root / 'crops'
            subprocess.run([sys.executable, str(ROOT / 'scripts/export_layers.py'), str(source), '--regions', str(regions), '--out', str(out)], check=True, capture_output=True)
            with Image.open(out / 'blue-block.png') as exported:
                self.assertEqual(exported.size, (30, 30))
                self.assertEqual(exported.getpixel((0, 0))[3], 0)
                self.assertEqual(exported.getpixel((10, 10))[3], 255)
            self.assertTrue((out / 'crop-manifest.json').exists())

    def test_visual_difference_and_size_guard(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            a = root / 'a.png'
            b = root / 'b.png'
            Image.new('RGB', (20, 10), '#ffffff').save(a)
            Image.new('RGB', (20, 10), '#000000').save(b)
            subprocess.run([sys.executable, str(ROOT / 'scripts/audit_visual.py'), '--reference', str(a), '--render', str(b), '--out', str(root / 'audit')], check=True, capture_output=True)
            report = json.loads((root / 'audit/report.json').read_text())
            self.assertEqual(report['mismatch_fraction'], 1)
            self.assertTrue((root / 'audit/overlay.png').exists())
            Image.new('RGB', (19, 10)).save(b)
            proc = subprocess.run([sys.executable, str(ROOT / 'scripts/audit_visual.py'), '--reference', str(a), '--render', str(b), '--out', str(root / 'audit2')], capture_output=True)
            self.assertNotEqual(proc.returncode, 0)

    def test_valid_spec(self):
        subprocess.run([sys.executable, str(ROOT / 'scripts/validate_spec.py'), str(ROOT / 'examples/design-spec.example.json')], check=True, capture_output=True)

    def test_invalid_outside_bounds(self):
        with tempfile.TemporaryDirectory() as td:
            spec = json.loads((ROOT / 'examples/design-spec.example.json').read_text())
            spec['layers'][0]['bounds'] = [1430, 0, 100, 5]
            target = Path(td) / 'bad.json'
            target.write_text(json.dumps(spec))
            proc = subprocess.run([sys.executable, str(ROOT / 'scripts/validate_spec.py'), str(target)], capture_output=True)
            self.assertNotEqual(proc.returncode, 0)




class PresentationTests(unittest.TestCase):
    """Presentation evidence must be composed from real captures, with provenance."""

    def _run(self, td, **kwargs):
        root = Path(td)
        sources = {}
        for key, size, color in (
            ('mobile', (390, 1020), '#235c9d'),
            ('tablet', (820, 1180), '#c46237'),
            ('desktop', (1440, 900), '#265d32'),
            ('reference', kwargs.get('reference_size', (1179, 616)), '#e0c521'),
            ('same', (1179, 616), '#265d32')
        ):
            dest = root / f'{key}.png'
            Image.new('RGB', size, color).save(dest)
            sources[key] = dest
        cmd = [sys.executable, str(ROOT / 'scripts/present_results.py'),
               '--mobile', str(sources['mobile']), '--tablet', str(sources['tablet']),
               '--desktop', str(sources['desktop']), '--out', str(root / 'presentation')]
        if kwargs.get('with_reference', True):
            cmd += ['--reference', str(sources['reference']), '--reference-kind', kwargs.get('kind', 'auto')]
        if kwargs.get('same_viewport', False):
            cmd += ['--desktop-reference-render', str(sources['same'])]
        subprocess.run(cmd, check=True, capture_output=True)
        return root / 'presentation'

    def test_paired_mobile_tablet_and_matching_desktop(self):
        with tempfile.TemporaryDirectory() as td:
            out = self._run(td, same_viewport=True)
            report = json.loads((out / 'presentation-report.json').read_text())
            self.assertTrue((out / 'mobile-tablet-side-by-side.png').exists())
            self.assertTrue((out / 'desktop-original-vs-render.png').exists())
            self.assertTrue(report['desktop_reference_viewport_match'])
            self.assertTrue(report['desktop_comparison_eligible_for_visual_audit'])
            self.assertEqual(len(report['outputs'][0]['panels']), 2)
            self.assertEqual(len(report['outputs'][1]['panels']), 2)

    def test_desktop_mismatch_is_flagged(self):
        with tempfile.TemporaryDirectory() as td:
            out = self._run(td)
            report = json.loads((out / 'presentation-report.json').read_text())
            self.assertFalse(report['desktop_reference_viewport_match'])
            self.assertFalse(report['desktop_comparison_eligible_for_visual_audit'])
            self.assertTrue(report['warnings'])
            self.assertTrue((out / 'desktop-original-vs-render.png').exists())

    def test_non_desktop_reference_has_desktop_preview(self):
        with tempfile.TemporaryDirectory() as td:
            out = self._run(td, kind='mobile', reference_size=(390, 844))
            report = json.loads((out / 'presentation-report.json').read_text())
            self.assertTrue((out / 'desktop-preview.png').exists())
            self.assertFalse((out / 'desktop-original-vs-render.png').exists())
            self.assertIsNone(report['desktop_reference_viewport_match'])

    def test_missing_capture_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            absent = root / 'missing.png'
            proc = subprocess.run([sys.executable, str(ROOT / 'scripts/present_results.py'),
                                   '--mobile', str(absent), '--tablet', str(absent),
                                   '--desktop', str(absent), '--out', str(root / 'out')], capture_output=True)
            self.assertNotEqual(proc.returncode, 0)


if __name__ == '__main__':
    unittest.main()

class ExtendedAuditTests(unittest.TestCase):
    """Guard against false-positive validations and misleading evidence images."""

    def test_mask_excludes_pixels_from_metrics_and_visuals(self):
        with tempfile.TemporaryDirectory() as td:
            from PIL import Image
            root = Path(td)
            a = root/'a.png'; b = root/'b.png'; masks = root/'masks.json'; out = root/'audit'
            Image.new('RGB', (10, 10), '#ffffff').save(a)
            Image.new('RGB', (10, 10), '#000000').save(b)
            masks.write_text(json.dumps({'exclude': [{'x': 0, 'y': 0, 'width': 10, 'height': 5}]}))
            subprocess.run([sys.executable, str(ROOT/'scripts/audit_visual.py'), '--reference', str(a), '--render', str(b), '--out', str(out), '--masks', str(masks)], check=True, capture_output=True)
            report = json.loads((out/'report.json').read_text())
            self.assertEqual(report['excluded_pixels'], 50)
            self.assertEqual(report['mismatch_pixels'], 50)
            self.assertEqual(report['mismatch_fraction'], 1)
            with Image.open(out/'threshold-diff.png') as img:
                self.assertEqual(img.getpixel((0, 0)), 0)
                self.assertEqual(img.getpixel((0, 8)), 255)
            with Image.open(out/'overlay.png') as img:
                self.assertEqual(img.getpixel((0, 0)), (188, 188, 188))

    def test_all_pixels_masked_is_not_valid_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); a = root/'a.png'; b = root/'b.png'
            Image.new('RGB', (2, 2)).save(a); Image.new('RGB', (2, 2)).save(b)
            mask = root/'mask.json'; mask.write_text(json.dumps({'exclude':[{'x':0,'y':0,'width':2,'height':2}]}))
            result = subprocess.run([sys.executable, str(ROOT/'scripts/audit_visual.py'), '--reference', str(a), '--render', str(b), '--out', str(root/'audit'), '--masks', str(mask)], capture_output=True)
            self.assertNotEqual(result.returncode, 0)

    def test_component_bounds_and_asset_path_rejected(self):
        from scripts.validate_spec import validate
        schema = json.loads((ROOT/'references/design-spec.schema.json').read_text())
        valid = json.loads((ROOT/'examples/design-spec.example.json').read_text())
        self.assertEqual(validate(valid, schema), [])
        bad = json.loads(json.dumps(valid)); bad['components'][0]['bounds'] = [20000, 0, 10, 10]
        self.assertTrue(any('component' in e for e in validate(bad, schema)))
        bad = json.loads(json.dumps(valid)); bad['assets'].append({'id': 'bad-asset', 'type': 'image', 'file': '../../secrets.txt', 'origin': 'test', 'usage': 'test', 'license': 'test', 'status': 'original-used', 'evidence': 'observed'})
        self.assertTrue(any('unsafe file path' in e for e in validate(bad, schema)))

    def test_cli_crop_boolean_tolerance_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); img = root/'a.png'; regions = root/'regions.json'
            Image.new('RGB', (8, 8), 'white').save(img)
            regions.write_text(json.dumps({'regions': [{'id': 'bad', 'bounds': [0, 0, 4, 4], 'remove_border_background': True, 'tolerance': True}]}))
            run = subprocess.run([sys.executable, str(ROOT/'scripts/export_layers.py'), str(img), '--regions', str(regions), '--out', str(root/'output')], capture_output=True)
            self.assertNotEqual(run.returncode, 0)

    def test_complete_image_pipeline(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); image=root/'reference.png'
            Image.new('RGB', (1179, 616), '#f8f8f8').save(image)
            regions=root/'regions.json'
            regions.write_text(json.dumps({'regions':[{'id':'background','bounds':[0,0,1179,616],'kind':'background'}]}))
            checks=[
                [sys.executable, str(ROOT/'scripts/image_inventory.py'), str(image), '--out', str(root/'inventory.json')],
                [sys.executable, str(ROOT/'scripts/export_layers.py'), str(image), '--regions', str(regions), '--out', str(root/'assets')],
                [sys.executable, str(ROOT/'scripts/validate_spec.py'), str(ROOT/'examples/design-spec.example.json')],
                [sys.executable, str(ROOT/'scripts/audit_visual.py'), '--reference', str(image), '--render', str(image), '--out', str(root/'audit')],
            ]
            for cmd in checks: subprocess.run(cmd, check=True, capture_output=True)
            self.assertEqual(json.loads((root/'audit/report.json').read_text())['mismatch_fraction'], 0)
            self.assertTrue((root/'assets/background.png').exists())
            self.assertTrue((root/'inventory.json').exists())


class StrictPresentationTests(unittest.TestCase):
    def test_mismatched_desktop_fails_quality_gate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for name, size in [('mobile', (390, 844)), ('tablet', (820, 1180)), ('desktop', (1440, 900)), ('original', (1179, 616))]:
                Image.new('RGB', size, 'white').save(root/f'{name}.png')
            cmd = [sys.executable, str(ROOT/'scripts/present_results.py'),
                   '--mobile', str(root/'mobile.png'), '--tablet', str(root/'tablet.png'),
                   '--desktop', str(root/'desktop.png'), '--reference', str(root/'original.png'),
                   '--reference-kind', 'desktop', '--require-matching-desktop', '--out', str(root/'report')]
            bad = subprocess.run(cmd, capture_output=True)
            self.assertNotEqual(bad.returncode, 0)
            self.assertFalse(json.loads((root/'report/presentation-report.json').read_text())['desktop_comparison_eligible_for_visual_audit'])
