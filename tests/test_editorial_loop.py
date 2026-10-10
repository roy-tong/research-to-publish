import tempfile
import unittest
from pathlib import Path
from test_pipeline import demo
from research_to_publish.core import Workspace, read_json, write_json
from research_to_publish.feedback import add, resolve, impact, route


class EditorialLoopTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.w = Workspace(Path(self.temp.name) / 'private')
        self.tid = demo.populate(self.w)

    def feedback(self, kind='counterevidence'):
        topic, _ = self.w.load(self.tid)
        data = {'id': 'reader-001', 'topic': self.tid, 'claim': topic['claims'][0]['id'],
                'kind': kind, 'text': 'Synthetic contradictory observation',
                'provenance': 'Synthetic test fixture, not a real reader',
                'next_action': 'Check original evidence and boundary'}
        p = Path(self.temp.name) / 'feedback.json'
        write_json(p, data)
        return p

    def test_single_channel_export_ignores_incomplete_other_drafts(self):
        route(self.w, self.tid, ['wechat'], 'Professional argument only')
        topic, ed = self.w.load(self.tid)
        del ed['site']; del ed['xiaohongshu']
        write_json(self.w.root / 'topics' / self.tid / 'editorial.json', ed)
        build = Path(self.w.build(self.tid)['build'])
        self.assertTrue((build / 'wechat.html').exists())
        self.assertFalse((build / 'site.md').exists())
        self.w.review(self.tid, 'test', 'synthetic review')
        out = Path(self.temp.name) / 'out'
        self.w.export(self.tid, out)
        self.assertEqual(read_json(out / 'release.json')['site_status'], 'not-staged')
        with self.assertRaisesRegex(ValueError, 'unselected'):
            self.w.record(self.tid, 'site', 'https://example.org/post', 'test')
        with self.assertRaisesRegex(ValueError, 'not selected'):
            self.w.export(self.tid, Path(self.temp.name) / 'bad', '/tmp/nonexistent-site')
        self.assertFalse((Path(self.temp.name) / 'bad').exists())

    def test_route_changes_invalidate_review_and_invalid_route_is_atomic(self):
        self.w.review(self.tid, 'test', 'test')
        before, _ = self.w.load(self.tid)
        with self.assertRaises(ValueError):
            route(self.w, self.tid, ['wechat', 'wechat'], 'bad')
        self.assertEqual(before, self.w.load(self.tid)[0])
        route(self.w, self.tid, ['site'], 'Archive only')
        self.assertFalse(self.w.approved(self.tid))

    def test_counterevidence_blocks_export_and_requires_new_review_after_resolution(self):
        self.w.build(self.tid)
        self.w.review(self.tid, 'test', 'test')
        add(self.w, self.feedback())
        self.assertFalse(self.w.approved(self.tid))
        with self.assertRaises(ValueError):
            self.w.export(self.tid, Path(self.temp.name) / 'out')
        with self.assertRaisesRegex(ValueError, 'counterevidence'):
            self.w.review(self.tid, 'test', 'test')
        resolve(self.w, 'reader-001', 'no-change', 'Original boundary already excludes this scenario')
        self.assertFalse(self.w.approved(self.tid))
        self.w.review(self.tid, 'test', 'Rechecked scope after feedback')
        self.assertTrue(self.w.approved(self.tid))

    def test_feedback_idempotency_conflict_and_no_fake_revision(self):
        p = self.feedback()
        a = add(self.w, p)
        self.assertEqual(a, add(self.w, p))
        with self.assertRaisesRegex(ValueError, 'unchanged'):
            resolve(self.w, 'reader-001', 'revised', 'Pretend revised')
        data = read_json(p); data['text'] = 'different'; write_json(p, data)
        with self.assertRaisesRegex(ValueError, 'different content'):
            add(self.w, p)
        topic, ed = self.w.load(self.tid)
        ed['site']['summary'] += ' Clarified boundary.'
        write_json(self.w.root / 'topics' / self.tid / 'editorial.json', ed)
        self.assertEqual(resolve(self.w, 'reader-001', 'revised', 'Boundary clarified')['state'], 'resolved')

    def test_question_is_not_counterevidence_and_private_feedback_not_exported(self):
        self.w.review(self.tid, 'test', 'test')
        p = self.feedback('question')
        add(self.w, p)
        self.assertTrue(self.w.approved(self.tid))
        self.w.build(self.tid)
        out = Path(self.temp.name) / 'out'
        self.w.export(self.tid, out)
        self.assertNotIn('Synthetic contradictory observation', ''.join(f.read_text() for f in out.rglob('*') if f.is_file()))

    def test_impact_finds_shared_source_and_publications(self):
        topic, ed = self.w.load(self.tid)
        sid = topic['sources'][0]
        self.w.review(self.tid, 'test', 'test')
        self.w.record(self.tid, 'wechat', 'https://example.org/wechat', 'Synthetic receipt')
        topic['id'] = 'second-treatment'
        write_json(self.w.root / 'topics/second-treatment/topic.json', topic)
        write_json(self.w.root / 'topics/second-treatment/editorial.json', ed)
        result = impact(self.w, sid)['topics']
        self.assertEqual(len(result), 2)
        first = next(r for r in result if r['topic'] == self.tid)
        self.assertTrue(first['affected_sections']['wechat'])
        self.assertEqual(len(first['publications']), 1)
        self.assertEqual(first['publications_need_revision'], [])
        with self.assertRaises((ValueError, OSError)):
            impact(self.w, 'absent-source')

    def test_unknown_feedback_claim_rejected(self):
        p = self.feedback(); data = read_json(p); data['claim'] = 'missing'; write_json(p, data)
        with self.assertRaisesRegex(ValueError, 'unknown claim'):
            add(self.w, p)
        self.assertFalse((self.w.root / 'feedback.json').exists())

    def test_all_channel_subsets_build_only_selected_artifacts(self):
        from itertools import combinations
        for size in (1, 2, 3):
            for channels in combinations(('site', 'wechat', 'xiaohongshu'), size):
                route(self.w, self.tid, list(channels), 'Synthetic routing coverage')
                out = Path(self.w.build(self.tid)['build'])
                for channel in ('site', 'wechat', 'xiaohongshu'):
                    self.assertEqual((out / (channel + '.md')).exists(), channel in channels)

    def test_pending_counterevidence_marks_published_content_for_recheck_and_enters_brief(self):
        self.w.review(self.tid, 'test', 'test')
        self.w.record(self.tid, 'wechat', 'https://example.org/synthetic', 'Synthetic receipt')
        add(self.w, self.feedback())
        self.assertEqual(len(self.w.status(self.tid)['publications_need_recheck']), 1)
        self.assertIn('Synthetic contradictory observation', Path(self.w.brief(self.tid)['brief']).read_text())


class LabelTest(unittest.TestCase):
    def test_public_reference_uses_label(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        w = Workspace(Path(temp.name) / 'private')
        tid = demo.populate(w)
        source = Path(temp.name) / 'public-note.md'
        source.write_text('Public research note with verifiable facts.')
        w.ingest('public-note', path=source, public='https://example.org/note/',
                 label='公开研究笔记（示例）')
        topic, _ = w.load(tid)
        topic['sources'].append('public-note')
        topic['claims'][0]['evidence'].append(
            {'source': 'public-note', 'quote': 'Public research note with verifiable facts.'})
        write_json(w.root / 'topics' / tid / 'topic.json', topic)
        build = Path(w.build(tid)['build'])
        text = (build / 'site.md').read_text(encoding='utf-8')
        self.assertIn('[公开研究笔记（示例）](https://example.org/note/)', text)
        self.assertNotIn('[public-note]', text)
