"""Private editorial decisions and operator-triaged feedback; no platform scraping."""
from .core import read_json, write_json, slug, nonempty, now, selected_channels


def route(workspace, tid, channels, reason):
    topic, _ = workspace.load(tid)
    topic['channels'] = channels
    selected_channels(topic)
    topic.setdefault('routing_history', []).append({
        'channels': channels, 'reason': nonempty(reason, 'routing reason'), 'at': now()})
    write_json(workspace.root / 'topics' / tid / 'topic.json', topic)
    return {'topic': tid, 'channels': selected_channels(topic), 'review_required': True}


def entries(workspace):
    workspace.require()
    path = workspace.root / 'feedback.json'
    return read_json(path) if path.exists() else []


def unresolved(workspace, tid):
    return [r for r in entries(workspace)
            if r['topic'] == tid and r['kind'] == 'counterevidence' and r['state'] == 'open']


def add(workspace, path):
    data = read_json(path)
    if not isinstance(data, dict):
        raise ValueError('Feedback must be a JSON object')
    allowed = {'id', 'topic', 'claim', 'kind', 'text', 'provenance', 'next_action'}
    if set(data) - allowed:
        raise ValueError('Unknown feedback fields; use the documented schema')
    fid, tid = slug(data.get('id')), slug(data.get('topic'))
    topic, _ = workspace.load(tid)
    claim = data.get('claim')
    if claim is not None and claim not in [c['id'] for c in topic['claims']]:
        raise ValueError('Feedback references an unknown claim')
    if data.get('kind') not in ('question', 'counterevidence', 'expression'):
        raise ValueError('kind must be question, counterevidence, or expression')
    for field in ('text', 'provenance', 'next_action'):
        nonempty(data.get(field), field)
    records = entries(workspace)
    for record in records:
        if record['id'] == fid:
            if record['input'] == data:
                return record
            raise ValueError('Feedback ID exists with different content; use a new ID')
    record = dict(data, input=data, state='open', created_at=now(),
                  baseline_fingerprint=workspace.fingerprint(tid))
    records.append(record)
    write_json(workspace.root / 'feedback.json', records)
    return record


def resolve(workspace, fid, decision, note):
    slug(fid)
    nonempty(note, 'resolution note')
    if decision not in ('revised', 'no-change'):
        raise ValueError('Unknown resolution decision')
    records = entries(workspace)
    record = next((r for r in records if r['id'] == fid), None)
    if record is None:
        raise ValueError('Unknown feedback ID')
    if record['state'] != 'open':
        raise ValueError('Feedback already resolved; preserve history and add new feedback')
    fp = workspace.fingerprint(record['topic'])
    if decision == 'revised' and fp == record['baseline_fingerprint']:
        raise ValueError('Content is unchanged; revised requires a new fingerprint')
    # Fingerprint change is not proof of a substantive correction; note is operator evidence.
    record.update(state='resolved', resolution={'decision': decision, 'note': note,
                  'at': now(), 'fingerprint': fp, 'verification': 'operator-attested'})
    write_json(workspace.root / 'feedback.json', records)
    # Even a no-change decision requires another explicit editorial review.
    review_path = workspace.root / 'topics' / record['topic'] / 'review.json'
    if record['kind'] == 'counterevidence' and review_path.exists():
        review = read_json(review_path)
        review['invalidated_by_feedback'] = fid
        review['fingerprint_before_invalidation'] = review.get('fingerprint')
        review['fingerprint'] = None
        write_json(review_path, review)
    return record


def impact(workspace, source=None):
    """Report source reuse and affected publication versions, without mutating them."""
    records = entries(workspace)
    if source is not None:
        workspace.source(source)
    rows = []
    for path in sorted((workspace.root / 'topics').glob('*/topic.json')):
        topic = read_json(path)
        tid = slug(topic['id'])
        if source is not None and source not in topic['sources']:
            continue
        status = workspace.status(tid)
        _, ed = workspace.load(tid)
        claims = [c['id'] for c in topic.get('claims', []) if source is None or
                  any(e['source'] == source for e in c['evidence'])]
        affected = {}
        for channel in selected_channels(topic):
            item = ed.get(channel, {})
            sections = item.get('sections', item.get('cards', []))
            affected[channel] = [i for i, s in enumerate(sections, 1)
                                 if set(s.get('claims', [])) & set(claims)]
        rows.append({'topic': tid, 'claims': claims, 'affected_sections': affected,
                     'local_sources_changed': status['local_sources_changed'],
                     'publications': status['publications'],
                     'publications_need_revision': status['publications_need_revision'],
                     'publications_need_recheck': status['publications_need_recheck'],
                     'reviewed': status['reviewed'],
                     'open_feedback': [r for r in records if r['topic'] == tid and r['state'] == 'open']})
    return {'topics': rows, 'note': 'Dependency candidates, not automatic factual conclusions. '
            'Feedback blocks its named topic; inspect other topics sharing its source. '
            'Records without publication receipts are unpublished.'}
