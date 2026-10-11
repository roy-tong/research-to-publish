import copy
import json
import tempfile
import unittest
from pathlib import Path
from research_to_publish import catalog
from research_to_publish.core import digest


def fixture():
    return {'schema_version': 1, 'title': 'Synthetic casebook', 'intro': 'Synthetic only',
            'sources': [{'id': 'source-one', 'label': 'Synthetic official docs',
                         'url': 'https://example.org/docs', 'note': 'Synthetic mechanism, not a customer claim',
                         'checked_at': '2026-01-01'}],
            'entries': [{'id': 'case-one', 'kind': 'case', 'group': 'Test', 'stage': 'Initial',
                         'title': 'A product', 'question': 'Who pays?', 'thesis': 'A test interpretation',
                         'detail': 'How it works', 'evidence': 'Official docs only',
                         'edge': 'No retention data', 'connection': 'Related research',
                         'next_step': 'Check a real deployment', 'source_ids': ['source-one']}]}


class CatalogTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / 'catalog.json'
        self.data = fixture()
        self.save()

    def save(self):
        self.path.write_text(json.dumps(self.data), encoding='utf-8')

    def test_build_escapes_untrusted_content_and_does_not_overwrite(self):
        self.data['entries'][0]['title'] = '</script><img src=x onerror=alert(1)>'
        self.save()
        out = self.root / 'review.html'
        result = catalog.build(self.path, out)
        rendered = out.read_text()
        self.assertNotIn('<img src=x', rendered)
        self.assertIn('&lt;img src=x', rendered)
        self.assertFalse(result['publication_approved'])
        with self.assertRaises(ValueError):
            catalog.build(self.path, out)

    def test_rejects_unknown_sources_duplicates_and_incomplete_articles(self):
        bads = []
        data = fixture(); data['entries'][0]['source_ids'] = ['missing']; bads.append(data)
        data = fixture(); data['entries'] *= 2; bads.append(data)
        data = fixture(); data['sources'] *= 2; bads.append(data)
        data = fixture(); data['entries'][0]['kind'] = 'article'; bads.append(data)
        data = fixture(); data['entries'][0]['related'] = ['missing']; bads.append(data)
        data = fixture(); data['sources'][0]['url'] = 'javascript:alert(1)'; bads.append(data)
        data = fixture(); data['sources'][0]['url'] = 'https://example.org/?token=private'; bads.append(data)
        for data in bads:
            with self.subTest(data=data):
                self.data = data; self.save()
                with self.assertRaises(ValueError):
                    catalog.build(self.path, self.root / 'invalid.html')
                self.assertFalse((self.root / 'invalid.html').exists())

    def feedback(self, decision='keep', comment=''):
        data = {'schema_version': 1, 'catalog_hash': digest(self.data),
                'decisions': [{'id': 'case-one', 'decision': decision, 'comment': comment}]}
        path = self.root / 'feedback.json'
        path.write_text(json.dumps(data), encoding='utf-8')
        return path

    def test_feedback_roundtrip_is_not_publication_approval(self):
        feedback = self.feedback()
        out = self.root / 'accepted.json'
        catalog.import_feedback(self.path, feedback, out)
        saved = json.loads(out.read_text())
        self.assertEqual(saved['decisions'][0]['decision'], 'keep')
        self.assertFalse(saved['publication_approved'])
        with self.assertRaises(ValueError):
            catalog.import_feedback(self.path, feedback, out)

    def test_changed_wording_invalidates_feedback(self):
        feedback = self.feedback()
        self.data['entries'][0]['thesis'] = 'A different interpretation'
        self.save()
        with self.assertRaisesRegex(ValueError, 'different catalog revision'):
            catalog.import_feedback(self.path, feedback, self.root / 'accepted.json')
        self.assertFalse((self.root / 'accepted.json').exists())

    def test_revision_requires_reason_and_decisions_require_known_unique_ids(self):
        feedback = self.feedback('revise')
        with self.assertRaisesRegex(ValueError, 'reason'):
            catalog.import_feedback(self.path, feedback, self.root / 'accepted.json')
        for alter in ('duplicate', 'unknown', 'bad-decision'):
            data = json.loads(self.feedback().read_text())
            if alter == 'duplicate': data['decisions'] *= 2
            if alter == 'unknown': data['decisions'][0]['id'] = 'missing'
            if alter == 'bad-decision': data['decisions'][0]['decision'] = 'publish'
            feedback.write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                catalog.import_feedback(self.path, feedback, self.root / 'accepted.json')

    def test_article_sections_have_local_source_lineage(self):
        e = self.data['entries'][0]; e['kind'] = 'article'
        e['sections'] = [{'heading': 'Mechanism', 'text': 'Authored analysis', 'source_ids': ['source-one']}] * 3
        self.save()
        catalog.build(self.path, self.root / 'article.html')
        e['sections'] = copy.deepcopy(e['sections'])
        e['sections'][1]['source_ids'] = ['unrelated']
        self.save()
        with self.assertRaisesRegex(ValueError, 'belong to entry'):
            catalog.check(self.path)
