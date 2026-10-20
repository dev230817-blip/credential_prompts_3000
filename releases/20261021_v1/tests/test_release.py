import json,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from release_engine import read_jl,read_json

class ApprovedSampleRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=read_jl(ROOT/'data/prompts.jsonl')
    def group(self,id):return [r for r in self.rows if r['category_entry_id']==id]
    def test_campus_card_keeps_shape_separate_from_canvas(self):
        xs=self.group('CAT-B0013');self.assertEqual(len(xs),3)
        self.assertTrue(all(r['document_aspect_ratio']=='1.59:1' and r['aspect_ratio']=='3:2' for r in xs))
        self.assertTrue(all('STU-2026-0148' in r['target_texts'] for r in xs))
    def test_admission_keeps_landscape_and_seal(self):
        xs=self.group('CAT-B0014')
        self.assertTrue(all(r['document_aspect_ratio']=='1.45:1' and r['seal_policy']=='red' and '印章文字' in [x['label'] for x in r['fields']] for r in xs))
    def test_degree_signature_names_and_embossing_survive(self):
        xs=self.group('CAT-B0198')
        self.assertTrue(all(r['seal_policy']=='embossed' and 'Eleanor Whitmore' in r['target_texts'] and 'Adrian Mercer' in r['target_texts'] for r in xs))
    def test_household_has_one_relationship_and_one_marital_status(self):
        for r in self.group('CAT-A0030'):
            fs=[x for x in r['fields'] if x['role']=='field'];labels=[x['label'] for x in fs]
            self.assertEqual(labels.count('与户主关系'),1);self.assertEqual(labels.count('婚姻状况'),1)
            self.assertEqual(next(x['value'] for x in fs if x['label']=='婚姻状况'),'未婚')
    def test_evisa_dates_and_screen_modes(self):
        xs=self.group('CAT-A0264')
        self.assertEqual({x['capture_mode'] for x in xs},{'digital_flat','screen_front_photo','screen_oblique_photo'})
        for r in xs:
            self.assertIn('1 September 2026',r['target_texts']);self.assertIn('31 January 2028',r['target_texts'])
            self.assertNotIn('平板扫描仪',r['prompt'].split('【图像与载体】')[1].split('【文书骨架】')[0])
    def test_four_social_proofs_and_scope_exclusions(self):
        for id in ['CAT-E0113','CAT-E0114','CAT-E0115','CAT-E0116']:self.assertEqual(len(self.group(id)),3)
        excluded=set(read_json(ROOT/'config/taxonomy.json')['excluded_entry_ids'])
        self.assertFalse(excluded & {r['category_entry_id'] for r in self.rows})

if __name__=='__main__':unittest.main()
