import unittest,sys,tempfile,json
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from advanced_visual_qa import build_mask,edge_alignment_hint,run
from audit_typography_icons import shape_metrics
from benchmark_evidence import summarize
from probe_agents import probe

class VisualGatesTests(unittest.TestCase):
 def test_ceiling(self):
  with self.assertRaises(ValueError):build_mask((100,100),[{'box':[0,0,40,40],'reason':'animated'}],.08)
 def test_ceiling_setting_cannot_exceed_eight_percent(self):
  with self.assertRaises(ValueError):build_mask((100,100),[],.5)
 def test_critical_region_protected(self):
  with self.assertRaises(ValueError):build_mask((100,100),[{'box':[5,5,15,15],'reason':'dynamic'}],.08,[[10,10,25,25]])
 def test_valid_mask(self):
  x,f=build_mask((100,100),[{'box':[0,0,20,20],'reason':'clock'}]);self.assertEqual(round(f,2),.04)
 def test_alignment_advisory(self):
  r=Image.new('RGB',(128,128),'white'); from PIL import ImageDraw
  d=ImageDraw.Draw(r);d.rectangle((30,30,80,80),fill='black')
  a=edge_alignment_hint(r,r)
  self.assertEqual(a['suggested_render_shift_px'],[0,0]);self.assertFalse(a['applied'])
 def test_report_contains_overlay_and_css_review(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);img=Image.new('RGB',(90,90),'white');img.save(p/'ref.png');img.save(p/'render.png')
   config={'reference':str(p/'ref.png'),'render':str(p/'render.png'),'regions':[{'name':'headline','priority':'critical','box':[10,10,60,35]}],
           'components':[{'selector':'.title','reference':{'x':10,'y':10,'width':50,'height':20},'actual':{'x':12,'y':13,'width':50,'height':20},'priority':'critical'}]}
   data=run(config,p/'out');self.assertTrue((p/'out/overlay.html').exists());self.assertTrue((p/'out/dashboard.md').exists())
   self.assertTrue(data['css_proposals'][0]['review_only']);self.assertEqual(data['regions'][0]['rgb_mae'],0)
 def test_missing_approval_never_passes(self):
  m={'projects':[{'name':'Catty','real_project':True,'approved_by_owner':True,'independent_references':False,'states':[]}]}
  self.assertFalse(summarize(m)['independent_benchmark_passed'])
 def test_negative_false_positive_rate(self):
  m={'projects':[{'name':'fixture','states':[],'negative_controls':[{'should_fail':True,'gate_failed':True},{'should_fail':True,'gate_failed':False}]}]}
  self.assertEqual(summarize(m)['negative_controls']['false_positive_rate'],.5)
 def test_agent_probe_no_false_pass(self):
  with tempfile.TemporaryDirectory() as t:
   r=probe(Path(t));self.assertIn('codex',r);self.assertNotEqual(r['codex']['runtime_invocation'],'PASS')
 def test_icon_identity(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);(p/'a.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"><path fill="black" d="M1 1h18v18H1z"/></svg>')
   r=shape_metrics(p/'a.svg',p/'a.svg');self.assertGreater(r['silhouette_iou'],.99)

if __name__=='__main__':unittest.main()

class ComponentGeometryTests(unittest.TestCase):
 def test_critical_tolerance_blocks_large_delta(self):
  from validate_component_geometry import check
  c={'components':[{'selector':'button','priority':'critical','reference':{'x':0,'y':0,'width':60,'height':40},'actual':{'x':5,'y':0,'width':60,'height':40}}]}
  self.assertFalse(check(c)['passed'])
 def test_critical_always_blocks_clipping(self):
  from validate_component_geometry import check
  c={'components':[{'selector':'button','priority':'critical','reference':{'x':0,'y':0,'width':60,'height':40},'actual':{'x':0,'y':0,'width':60,'height':40},'clipped':True,'tolerance_px':30}]}
  self.assertFalse(check(c)['passed'])

class NegativeControlTests(unittest.TestCase):
 def test_all_synthetic_negative_controls_caught(self):
  from negative_controls import execute
  x=execute()
  self.assertEqual(x['total'],4);self.assertEqual(x['caught'],4)