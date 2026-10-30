"""Pixel QA regression: dimensions, multi-state, provenance, baseline and outputs."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from PIL import Image, ImageDraw
from scripts.calibrate_pixel_perfect import crop_panels, compare_states, metrics

ROOT=Path(__file__).resolve().parents[1]

class PixelCalibrationTests(unittest.TestCase):
    def test_identical_and_different_metrics(self):
        ref=Image.new('RGB',(40,40),'white')
        self.assertEqual(metrics(ref,ref)['mean_absolute_error_rgb'],0)
        self.assertEqual(metrics(ref,ref)['mismatch_fraction_over_threshold'],0)
        other=Image.new('RGB',(40,40),'black')
        self.assertGreater(metrics(ref,other)['mean_absolute_error_rgb'],200)

    def test_three_states_outputs_and_baseline_delta(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'out'
            refs=[Image.new('RGB',(48,80),'white') for _ in range(3)]
            curr=[Image.new('RGB',(48,80),'white') for _ in range(3)]
            before=[Image.new('RGB',(48,80),'black') for _ in range(3)]
            report=compare_states(refs,curr,out,before)
            self.assertEqual(len(report['states']),3)
            self.assertEqual(report['average_mae'],0)
            self.assertTrue(all(x['change']['mae_delta']<0 for x in report['states']))
            for i in (1,2,3):
                self.assertTrue((out/f'compare-state-{i}.png').exists())
                self.assertTrue((out/f'heatmap-state-{i}.png').exists())
            self.assertIn('a 0-10',report['note'])

    def test_geometry_mismatch_hard_failure_without_normalization(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,'same viewport|normalize-reference'):
                compare_states([Image.new('RGB',(100,100))],[Image.new('RGB',(90,90))],Path(td)/'bad')
            report=compare_states([Image.new('RGB',(100,100),'white')],[Image.new('RGB',(90,90),'white')],Path(td)/'good',normalize=True)
            self.assertTrue(report['states'][0]['reference_normalized'])

    def test_panels_require_exact_integer_division(self):
        self.assertEqual([x.size for x in crop_panels(Image.new('RGB',(120,80)),3)],[(40,80)]*3)
        with self.assertRaises(ValueError): crop_panels(Image.new('RGB',(121,80)),3)

    def test_cli_triptych_requires_explicit_normalize(self):
        with tempfile.TemporaryDirectory() as td:
            d=Path(td)
            Image.new('RGB',(120,80),'white').save(d/'triptych.png')
            for i in (1,2,3):Image.new('RGB',(30,60),'white').save(d/f'{i}.png')
            cmd=[sys.executable,str(ROOT/'scripts/calibrate_pixel_perfect.py'), '--reference',str(d/'triptych.png'),'--columns','3',
                 '--out',str(d/'out'),*[item for i in (1,2,3) for item in ('--render',str(d/f'{i}.png'))]]
            bad=subprocess.run(cmd,capture_output=True,text=True)
            self.assertNotEqual(bad.returncode,0)
            yes=subprocess.run(cmd+['--normalize-reference'],capture_output=True,text=True)
            self.assertEqual(yes.returncode,0,yes.stderr)
            self.assertEqual(len(json.loads((d/'out/calibration-metrics.json').read_text())['states']),3)

if __name__=='__main__':unittest.main()
