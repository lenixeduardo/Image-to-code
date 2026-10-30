import sys
import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from ci_metrics import collect_from_log,aggregate,make_record,validate,write_outputs
from tempfile import TemporaryDirectory

class MetricsTests(unittest.TestCase):
 def test_extract_counts(self):
  rec=collect_from_log('Ran 72 tests in 1.2s\n\nOK\n# tests 5\n# pass 5\n','tests',13,'0'*40)
  self.assertEqual(rec['python_passed'],72);self.assertEqual(rec['js_passed'],5)
 def test_no_artifact_is_unknown(self):
  run={'id':10,'head_sha':'1'*40,'created_at':'2026-10-30T00:00:00Z','status':'completed','conclusion':'success','html_url':'https://example.com'}
  x=aggregate([run],{})['runs'][0]
  self.assertIsNone(x['python_passed']);self.assertFalse(x['metrics_available'])
 def test_validated_metrics(self):
  rec=make_record(sha='1'*40,python_total=4,python_passed=4)
  run={'id':10,'head_sha':'1'*40,'created_at':'2026-10-30T00:00:00Z','conclusion':'success'}
  x=aggregate([run],{10:[rec]})['runs'][0]
  self.assertEqual(x['python_total'],4)
 def test_malformed_rejected(self):
  with self.assertRaises(ValueError): validate({'schema_version':1,'python_total':1,'python_passed':2})
 def test_dashboard_export(self):
  with TemporaryDirectory() as td:
   p=Path(td); x=aggregate([],{});self.assertEqual(len(write_outputs(x,p)),4)
   self.assertIn('N/D',(p/'history.md').read_text())

if __name__=='__main__':unittest.main()