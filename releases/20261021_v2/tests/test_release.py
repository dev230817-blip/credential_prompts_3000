from pathlib import Path
import copy,json,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from release_engine import read_jl,read_json,core_payload,canonical,sha,render

class PolicyARegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=read_jl(ROOT/'data/prompts.jsonl');cls.bases=read_jl(ROOT/'data/base_values_1430.jsonl');cls.config=read_json(ROOT/'config/imaging_rules.json')
    def group(self,entry):return [r for r in self.rows if r['category_entry_id']==entry]
    def test_option_A_is_not_a_full_text_or_layout_lock(self):
        for r in self.rows:
            self.assertFalse(r['layout_locked']);self.assertFalse(r['full_visible_text_locked']);self.assertEqual(r['target_texts_scope'],'supplied_core_values_only');self.assertIsNone(r['document_aspect_ratio'])
    def test_core_digest_detects_a_changed_value(self):
        b=copy.deepcopy(self.bases[0]);original=b['core_values_sha256'];b['core_fields'][0]['value']+=' changed'
        self.assertNotEqual(original,sha(canonical(core_payload(b)).encode()))
    def test_degree_has_fictional_signers_but_no_inherited_engraving_or_ratio(self):
        for r in self.group('CAT-B0198'):
            self.assertIn('Eleanor Whitmore',r['target_texts']);self.assertIn('Adrian Mercer',r['target_texts'])
            self.assertNotIn('页面下部有低对比度圆形机构压印',r['prompt']);self.assertNotIn('文档本体宽:高=',r['prompt']);self.assertNotIn('This is to certify that Maya Elena Hart',r['target_texts'])
    def test_household_keeps_values_without_seven_row_skeleton(self):
        for r in self.group('CAT-A0030'):
            self.assertEqual(r['expected_core_values']['婚姻状况'],'未婚');self.assertEqual(r['expected_core_values']['与户主关系'],'子');self.assertNotIn('表格每行依次为',r['prompt']);self.assertNotIn('登记专用章',r['target_texts'])
    def test_hong_kong_trial_values_and_no_fake_number(self):
        for r in self.group('CAT-D0081'):
            self.assertIn('CLEARFIELD ENGINEERING SERVICES LIMITED',r['target_texts']);self.assertIn('15 April 2027',r['target_texts']);self.assertNotIn('76543210',r['prompt']);self.assertNotIn('留空',r['prompt']);self.assertNotIn('***',r['target_texts'])
    def test_cfp_is_electronic_and_has_no_added_signer(self):
        xs=self.group('CAT-C0207');self.assertEqual({r['capture_mode'] for r in xs},{'digital_flat','screen_front_photo','screen_oblique_photo'})
        for r in xs:
            self.assertIn('CFP® CERTIFICATION',r['target_texts']);self.assertIn('Adrian Cole Bennett',r['target_texts']);self.assertFalse(any('signatory' in f['label'].lower() for f in r['core_fields']));self.assertNotIn('平板扫描仪',r['prompt'])
    def test_camera_paragraphs_only_are_switched(self):
        b=self.bases[0];a=render(b,'scan',self.config);c=render(b,'oblique_photo',self.config)
        self.assertEqual(a.split('【本条成像要求】')[0],c.split('【本条成像要求】')[0]);self.assertNotEqual(a,c)
    def test_scoped_changes_are_only_two_trial_categories(self):
        report=read_json(ROOT/'reports/parent_value_comparison.json');self.assertEqual(report['core_field_sets_unchanged'],1428);self.assertEqual(set(report['trial_example_overrides']),{'CAT-C0207','CAT-D0081'})
    def test_social_proofs_retained_and_excluded_categories_stay_out(self):
        for entry in ['CAT-E0113','CAT-E0114','CAT-E0115','CAT-E0116']:self.assertEqual(len(self.group(entry)),3)
        excluded=set(read_json(ROOT/'config/taxonomy.json')['excluded_entry_ids']);self.assertFalse(excluded & {r['category_entry_id'] for r in self.rows})

if __name__=='__main__':unittest.main()
