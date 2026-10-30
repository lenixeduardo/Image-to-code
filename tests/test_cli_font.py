import sys
import json
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from prepare_cli_environments import prepare, CATALOG
from verify_font_identity import audit

class CLIPreflightTests(unittest.TestCase):
    def test_layouts_are_created_without_install(self):
        with tempfile.TemporaryDirectory() as td:
            r=Path(td);(r/'SKILL.md').write_text('---\nname: image-to-code\n---\n')
            x=prepare(r,r/'out',['claude-code','codex','opencode','freebuff','hermes','cursor'],False,False)
            self.assertEqual(len(x['placements']),6)
            self.assertTrue(all(a['skill_discoverable'] for a in x['placements']))
            self.assertTrue(all(a['invocation']=='NOT_AUTHENTICATED' for a in x['agents']))

    def test_font_missing_is_unverified(self):
        with tempfile.TemporaryDirectory() as td:
            r=audit({'fonts':[{'id':'example','approved_original':'missing.woff2','candidate':'missing2.woff2'}]},Path(td))
            self.assertFalse(r['verified']);self.assertEqual(r['fonts'][0]['status'],'ORIGINAL_UNAVAILABLE')

    def test_font_hash_proves_identity(self):
        from fontTools.fontBuilder import FontBuilder
        from fontTools.pens.ttGlyphPen import TTGlyphPen
        with tempfile.TemporaryDirectory() as td:
            p=Path(td); f=FontBuilder(1000,isTTF=True);f.setupGlyphOrder(['.notdef','A']);g=TTGlyphPen(None).glyph();f.setupGlyf({'.notdef':g,'A':g});f.setupCharacterMap({65:'A'});f.setupHorizontalMetrics({'.notdef':(500,0),'A':(500,0)});f.setupHorizontalHeader(ascent=800,descent=-200);f.setupNameTable({'familyName':'QA Test Font','styleName':'Regular','uniqueFontIdentifier':'QA','fullName':'QA Test Font','psName':'QATestFont'});f.setupOS2();f.setupPost();f.setupMaxp();f.save(p/'a.ttf');(p/'b.ttf').write_bytes((p/'a.ttf').read_bytes())
            x=audit({'fonts':[{'id':'test','approved_original':'a.ttf','candidate':'b.ttf'}]},p)
            self.assertTrue(x['verified']);self.assertEqual(x['fonts'][0]['status'],'IDENTICAL_BYTES')
            (p/'b.ttf').write_bytes((p/'b.ttf').read_bytes()+b'not identical')
            y=audit({'fonts':[{'id':'test','approved_original':'a.ttf','candidate':'b.ttf'}]},p)
            self.assertFalse(y['verified'])

if __name__=='__main__':unittest.main()