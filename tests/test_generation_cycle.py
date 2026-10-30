from __future__ import annotations
import importlib.util
import tempfile
import unittest
from pathlib import Path

from PIL import Image

P = Path(__file__).resolve().parents[1] / 'scripts' / 'validate_generation_cycle.py'
spec = importlib.util.spec_from_file_location('validate_generation_cycle', P)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class GenerationCycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for fname, color in [('full.png','blue'),('crop.png','red'),('generated.png','green'),('final.png','purple'),('evidence.png','yellow')]:
            Image.new('RGB',(512,768),color).save(self.root/fname)
        (self.root/'prompt.md').write_text('## Identity\n'+('The quadrupedal kitten has cream fur, amber eyes, and a silver heart. '*12)+'\n## Anatomy\nVisible front paws.\n## Lighting\nBaked red coral light.\n## Composition\nVertical frame.\n## Exclusions\nNo UI or text.')
        (self.root/'type.json').write_text('{}')
        reviews={k:{'status':'pass','notes':'Checked exact reference and regenerated artwork, no visible divergence.','evidence':['evidence.png']} for k in module.REVIEWS}
        self.contract={'workflow':'reference_guided_two_stage_generation','reference':{'full_screenshot':'full.png','component_crop':'crop.png','crop_box':[0,0,512,768],'crop_usage':'generation_reference_only'},'scene':{'origin':'image_generation_with_reference','prompt_path':'prompt.md','generated_image':'generated.png','text_free':True,'baked_lighting':True,'duplicate_css_glow':False,'conditioned_on':['full.png','crop.png']},'attempts':[{'generated_image':'generated.png','status':'accepted'}],'reviews':reviews,'typography_stage':{'mode':'live_html_css_overlay','spec_path':'type.json','final_render':'final.png','exact_copy':['Seu inglês tá uma merda? A Catty resolve.'],'preserved_scene':True,'layout_checked':True}}

    def test_complete_documented_two_stage_passes(self):
        self.assertEqual(module.validate(self.contract,self.root),[])

    def test_crop_not_accepted_as_final_asset(self):
        self.contract['scene']['generated_image']='crop.png'
        self.contract['attempts'][0]['generated_image']='crop.png'
        self.assertTrue(any('byte-identical' in x for x in module.validate(self.contract,self.root)))

    def test_missing_visual_reference_is_blocker(self):
        self.contract['scene']['conditioned_on']=['full.png']
        self.assertTrue(any('conditioned_on' in x for x in module.validate(self.contract,self.root)))

    def test_baked_ui_text_during_scene_stage_rejected(self):
        self.contract['scene']['text_free']=False
        self.assertTrue(any('text_free' in x for x in module.validate(self.contract,self.root)))

    def test_unrelated_duplicate_css_light_rejected(self):
        self.contract['scene']['duplicate_css_glow']=True
        self.assertTrue(any('baked_lighting' in x for x in module.validate(self.contract,self.root)))

    def test_paw_missing_rejects(self):
        self.contract['reviews']['anatomy_paws']['status']='fail'
        self.assertTrue(any('anatomy_paws' in x for x in module.validate(self.contract,self.root)))

    def test_unvalidated_typography_rejects(self):
        self.contract['typography_stage']['layout_checked']=False
        self.assertTrue(any('layout_checked' in x for x in module.validate(self.contract,self.root)))

    def test_missing_attempt_reason_rejected(self):
        self.contract['attempts'].insert(0,{'status':'rejected','generated_image':'full.png'})
        self.assertTrue(any('rejection notes' in x for x in module.validate(self.contract,self.root)))

    def test_path_escape_rejected(self):
        self.contract['scene']['generated_image']='../outside.png'
        self.assertTrue(any('unsafe relative' in x for x in module.validate(self.contract,self.root)))

    def test_second_image_pass_allowed(self):
        self.contract['typography_stage']['mode']='second_image_edit_pass'
        self.assertEqual(module.validate(self.contract,self.root),[])

if __name__ == '__main__':unittest.main()
