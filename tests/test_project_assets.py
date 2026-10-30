import tempfile
from pathlib import Path
import unittest
from scripts.audit_project_assets import audit


class TestProjectAssets(unittest.TestCase):
    def test_original_missing_even_with_fallback(self):
        with tempfile.TemporaryDirectory() as name:
            project = Path(name)
            (project/'src').mkdir()
            (project/'public').mkdir()
            (project/'public/catty.png').write_bytes(b'\x89PNG')
            (project/'src/Catty.tsx').write_text('''<img src="/assets/catty/hero.webp" onError={e=>e.currentTarget.src="/catty.png"} />''')
            result = audit(project)
            self.assertFalse(result['passed'])
            self.assertEqual(len(result['missing']), 1)
            self.assertEqual(result['missing'][0]['url'], '/assets/catty/hero.webp')
    def test_valid_assets_and_external_image_ignored(self):
        with tempfile.TemporaryDirectory() as name:
            project = Path(name)
            (project/'src').mkdir()
            (project/'public/icons').mkdir(parents=True)
            (project/'public/icons/cat.svg').write_text('<svg/>')
            (project/'src/page.tsx').write_text('''<img src="/icons/cat.svg"/> <img src="https://cdn.example.test/cat.png"/>''')
            result=audit(project)
            self.assertTrue(result['passed'])
            self.assertEqual(len(result['references']),1)
    def test_escape_is_blocked(self):
        with tempfile.TemporaryDirectory() as name:
            project=Path(name)
            (project/'src').mkdir()
            (project/'public').mkdir()
            (project/'src/a.tsx').write_text('''<img src="/../../unsafe.svg"/>''')
            result=audit(project)
            self.assertFalse(result['passed'])
            self.assertEqual(result['missing'][0]['status'],'unsafe')

if __name__=='__main__':unittest.main()