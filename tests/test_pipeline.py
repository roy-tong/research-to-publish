import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from research_to_publish.core import Workspace, chatgpt_text, read_json, write_json

spec = importlib.util.spec_from_file_location('demo', Path(__file__).resolve().parents[1] / 'examples/demo.py')
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


class PipelineTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.w = Workspace(Path(self.temp.name) / 'private')
        self.tid = demo.populate(self.w)

    def test_end_to_end_and_no_raw_source_export(self):
        build = self.w.build(self.tid)
        self.assertFalse(build['reviewed'])
        with self.assertRaises(ValueError):
            self.w.export(self.tid, Path(self.temp.name) / 'out')
        self.w.review(self.tid, 'test reviewer', 'Synthetic fixture checked')
        out = Path(self.temp.name) / 'out'
        result = self.w.export(self.tid, out)
        self.assertFalse(result['published'])
        self.assertTrue((out / 'cards/01.svg').exists())
        self.assertFalse((out / 'manifest.json').exists())
        # Compare against the resolved workspace root: on macOS the temp dir
        # symlink (/var -> /private/var) would otherwise hide leaked paths.
        self.assertNotIn(str(self.w.root), ''.join(p.read_text() for p in out.rglob('*') if p.is_file()))

    def test_editorial_change_invalidates_review(self):
        self.w.review(self.tid, 'test', 'checked')
        p = self.w.root / 'topics' / self.tid / 'editorial.json'
        data = read_json(p)
        data['site']['summary'] += ' 修订。'
        write_json(p, data)
        self.assertFalse(self.w.approved(self.tid))

    def test_source_change_requires_reingest(self):
        source = Path(self.temp.name) / 'input.md'
        source.write_text('old evidence')
        self.w.ingest('local', path=source)
        topic, _ = self.w.load(self.tid)
        topic['sources'].append('local')
        write_json(self.w.root / 'topics' / self.tid / 'topic.json', topic)
        self.w.review(self.tid, 'test', 'checked')
        source.write_text('new evidence')
        self.assertEqual(self.w.status(self.tid)['local_sources_changed'], ['local'])
        self.assertFalse(self.w.status(self.tid)['reviewed'])
        with self.assertRaisesRegex(ValueError, 're-ingest'):
            self.w.build(self.tid)
        self.w.ingest('local', path=source)
        self.assertFalse(self.w.approved(self.tid))

    def test_unknown_claim_and_fake_quote_rejected(self):
        topic, ed = self.w.load(self.tid)
        topic['claims'][0]['evidence'][0]['quote'] = 'fabricated quote'
        write_json(self.w.root / 'topics' / self.tid / 'topic.json', topic)
        with self.assertRaisesRegex(ValueError, 'excerpt'):
            self.w.validate(self.tid)

    def test_chatgpt_not_factual_proof(self):
        topic, _ = self.w.load(self.tid)
        topic['claims'][0]['kind'] = 'fact'
        write_json(self.w.root / 'topics' / self.tid / 'topic.json', topic)
        with self.assertRaisesRegex(ValueError, 'primary'):
            self.w.validate(self.tid)

    def test_tampered_build_rejected(self):
        out = Path(self.w.build(self.tid)['build'])
        self.w.review(self.tid, 'test', 'checked')
        (out / 'site.md').write_text('tampered')
        with self.assertRaisesRegex(ValueError, 'modified'):
            self.w.export(self.tid, Path(self.temp.name) / 'out')
        self.assertFalse((Path(self.temp.name) / 'out').exists())

    def test_staging_never_overwrites_post(self):
        self.w.build(self.tid)
        self.w.review(self.tid, 'test', 'checked')
        site = Path(self.temp.name) / 'site'
        (site / '_posts').mkdir(parents=True)
        (site / '_config.yml').write_text('title: Test')
        post = site / '_posts' / ('2026-10-09-' + self.tid + '.md')
        post.write_text('keep user edit')
        with self.assertRaisesRegex(ValueError, 'overwrite'):
            self.w.export(self.tid, Path(self.temp.name) / 'out', site)
        self.assertEqual(post.read_text(), 'keep user edit')

    def test_deterministic_build_and_escape(self):
        _, ed = self.w.load(self.tid)
        ed['wechat']['sections'][0]['body'] = '<script>alert(1)</script>'
        write_json(self.w.root / 'topics' / self.tid / 'editorial.json', ed)
        a = self.w.build(self.tid)
        b = self.w.build(self.tid)
        self.assertEqual(a, b)
        self.assertNotIn('<script>', (Path(a['build']) / 'wechat.html').read_text())

    def test_selected_export_branch_only(self):
        data = {'id': 'one', 'current_node': 'b', 'mapping': {
          'root': {'parent': None, 'message': None},
          'a': {'parent': 'root', 'message': {'author': {'role': 'user'}, 'content': {'parts': ['question']}}},
          'b': {'parent': 'a', 'message': {'author': {'role': 'assistant'}, 'content': {'parts': ['selected']}}},
          'c': {'parent': 'a', 'message': {'author': {'role': 'assistant'}, 'content': {'parts': ['discarded']}}}}}
        text, meta = chatgpt_text(data)
        self.assertIn('selected', text)
        self.assertNotIn('discarded', text)
        with self.assertRaises(ValueError):
            chatgpt_text([data, dict(data, id='two')])

    def test_github_requires_immutable_commit(self):
        with self.assertRaisesRegex(ValueError, 'immutable'):
            self.w.ingest('github', repo='owner/repo', ref='main', github_path='README.md')

    def test_path_traversal_rejected(self):
        with self.assertRaises(ValueError):
            self.w.create_topic('../escape', 'Title', 'Question', ['demo-source'])

    def test_publication_receipt_tracks_revision(self):
        self.w.review(self.tid, 'test', 'checked')
        self.w.record(self.tid, 'site', 'https://example.com/notes/demo/', 'Verified by test operator')
        topic, ed = self.w.load(self.tid)
        ed['site']['summary'] += 'changed'
        write_json(self.w.root / 'topics' / self.tid / 'editorial.json', ed)
        self.assertEqual(len(self.w.status(self.tid)['publications_need_revision']), 1)


    def test_site_stage_is_not_publication(self):
        self.w.build(self.tid)
        self.w.review(self.tid, 'test', 'checked')
        site = Path(self.temp.name) / 'site'
        (site / '_posts').mkdir(parents=True)
        (site / '_config.yml').write_text('title: Test')
        result = self.w.export(self.tid, Path(self.temp.name) / 'out', site)
        self.assertFalse(result['published'])
        self.assertIn('layout: "post"', Path(result['site_file']).read_text())
        self.assertEqual(self.w.status(self.tid)['publications'], [])

    def test_idempotent_sync_and_public_metadata_changes(self):
        p = Path(self.temp.name) / 'source.txt'
        p.write_text('version one')
        config = Path(self.temp.name) / 'sources.json'
        write_json(config, {'schema_version': 1, 'sources': [{'id': 'synced', 'path': 'source.txt'}]})
        self.assertTrue(self.w.sync(config)['sources'][0]['changed'])
        first = self.w.source('synced')
        self.assertFalse(self.w.sync(config)['sources'][0]['changed'])
        self.assertEqual(first, self.w.source('synced'))
        p.write_text('version two')
        self.assertTrue(self.w.sync(config)['sources'][0]['changed'])
        self.assertTrue((self.w.root / first['snapshot']).exists())

    def test_github_download_metadata(self):
        import io
        with patch('urllib.request.urlopen', return_value=io.BytesIO(b'fixed commit content')) as get:
            source = self.w.ingest('remote', repo='owner/repo', ref='a'*40, github_path='docs/file.md')
        self.assertEqual(source['origin']['ref'], 'a'*40)
        self.assertIn('raw.githubusercontent.com/owner/repo/', get.call_args[0][0])

    def test_card_overflow_fails_build(self):
        topic, ed = self.w.load(self.tid)
        ed['xiaohongshu']['cards'][0]['body'] = 'word '*500
        write_json(self.w.root / 'topics' / self.tid / 'editorial.json', ed)
        with self.assertRaisesRegex(ValueError, 'overflows'):
            self.w.build(self.tid)

    def test_duplicate_publication_receipt_is_idempotent(self):
        self.w.review(self.tid, 'test', 'checked')
        for _ in range(2):
            self.w.record(self.tid, 'site', 'https://example.com/notes/demo/', 'checked')
        self.assertEqual(len(self.w.status(self.tid)['publications']), 1)

    def test_custom_site_requires_existing_knowledge_mapping(self):
        site = Path(self.temp.name) / 'site'
        (site / '_posts').mkdir(parents=True)
        (site / '_data').mkdir()
        (site / '_knowledge').mkdir()
        (site / '_config.yml').write_text('title: Test')
        write_json(site / '_data/knowledge_topics.json', [{'id': 'research'}])
        (site / '_knowledge/evidence.md').write_text('existing knowledge')
        self.w.build(self.tid)
        self.w.review(self.tid, 'test', 'checked')
        with self.assertRaisesRegex(ValueError, 'knowledge_topic'):
            self.w.export(self.tid, Path(self.temp.name) / 'blocked', site)
        self.assertFalse((Path(self.temp.name) / 'blocked').exists())
        topic, ed = self.w.load(self.tid)
        ed['site'].update(knowledge_topic='research', knowledge_units=['evidence'])
        write_json(self.w.root / 'topics' / self.tid / 'editorial.json', ed)
        build = self.w.build(self.tid)
        self.assertIn('knowledge_units: ["evidence"]', (Path(build['build']) / 'site.md').read_text())
        self.w.review(self.tid, 'test', 'checked')
        self.assertTrue(self.w.export(self.tid, Path(self.temp.name) / 'ready', site)['site_file'])

if __name__ == '__main__':
    unittest.main()
