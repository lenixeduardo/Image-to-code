from __future__ import annotations
import importlib.util
import tempfile
import unittest
from pathlib import Path
from PIL import Image

SCRIPT=Path(__file__).resolve().parents[1]/'scripts/prepare_generation_reference.py'
spec=importlib.util.spec_from_file_location('prepare_generation_reference',SCRIPT)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class ReferenceCropTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.root=Path(self.temp.name)
  self.original=self.root/'input.png'
  Image.new('RGB',(900,1200),'#ee2244').save(self.original)
 def test_crop_is_exact_and_flagged_reference_only(self):
  out=self.root/'artifacts/reference/catty.png'
  result=module.exact_crop(self.original,out,(110,80,400,450))
  with Image.open(out) as im:
   self.assertEqual(im.size,(400,450))
  self.assertEqual(result['crop_usage'],'generation_reference_only')
  self.assertEqual(result['source_dimensions'],[900,1200])
 def test_out_of_bounds_crop_rejected(self):
  with self.assertRaisesRegex(ValueError,'bounds'):
   module.exact_crop(self.original,self.root/'crop.png',(700,800,400,500))
 def test_zero_width_rejected(self):
  with self.assertRaises(ValueError):
   module.exact_crop(self.original,self.root/'crop.png',(0,0,0,400))
if __name__=='__main__':unittest.main()
