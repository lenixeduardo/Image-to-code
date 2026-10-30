import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/validate_visual_review.py'
spec = importlib.util.spec_from_file_location('visual_review', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class VisualReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'comparison.png').write_bytes(b'placeholder')
        self.item = {'status':'pass','evidence':['comparison.png'],'notes':'Compared screenshot with exact matching viewport'}
        self.reviews = {'reviews': {k: self.item.copy() for k in module.REQUIRED}}

    def test_four_valid_evidence_entries_accepted(self):
        self.assertEqual(module.check(self.reviews, self.root), [])

    def test_missing_icon_review_is_not_approved(self):
        del self.reviews['reviews']['icons']
        self.assertTrue(any('icons' in x for x in module.check(self.reviews, self.root)))

    def test_subject_anatomy_failure_blocks_approval(self):
        self.reviews['reviews']['subject_integrity']['status']='fail'
        self.assertTrue(any('subject_integrity' in x for x in module.check(self.reviews, self.root)))

    def test_baked_light_uncertainty_blocks_approval(self):
        self.reviews['reviews']['lighting_composition']['status']='unknown'
        self.assertTrue(any('lighting_composition' in x for x in module.check(self.reviews, self.root)))

    def test_missing_or_escaping_evidence_blocked(self):
        self.reviews['reviews']['icons']['evidence']=['../secret.png']
        self.assertTrue(module.check(self.reviews, self.root))
        self.reviews['reviews']['icons']['evidence']=['not-there.png']
        self.assertTrue(module.check(self.reviews, self.root))

    def test_short_notes_not_accepted(self):
        self.reviews['reviews']['typography_controls']['notes']='ok'
        self.assertTrue(module.check(self.reviews, self.root))


if __name__ == '__main__':unittest.main()
