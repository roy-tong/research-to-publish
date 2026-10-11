"""Private editorial casebooks. Review choices never approve publication."""
import html
import json
from collections import Counter
from pathlib import Path
from .core import digest, nonempty, public_url, read_json, slug

KINDS = {'case': '案例', 'article': '文章成稿', 'pitch': '选题', 'strategy': '渠道策略'}
DECISIONS = {'pending': '待审', 'keep': '保留', 'revise': '修改', 'drop': '暂缓'}


def load_catalog(path):
    data = read_json(path)
    if not isinstance(data, dict) or data.get('schema_version') != 1:
        raise ValueError('catalog schema_version must be 1')
    for field in ('title', 'intro'):
        nonempty(data.get(field), field)
    sources = data.get('sources')
    entries = data.get('entries')
    if not isinstance(sources, list) or not isinstance(entries, list) or not entries:
        raise ValueError('catalog requires sources and non-empty entries lists')
    source_ids = set()
    for s in sources:
        if not isinstance(s, dict):
            raise ValueError('source must be an object')
        sid = slug(s.get('id'))
        if sid in source_ids:
            raise ValueError('duplicate source ID: ' + sid)
        source_ids.add(sid)
        public_url(s.get('url', ''))
        for field in ('label', 'note', 'checked_at'):
            nonempty(s.get(field), 'source ' + field)
    ids = set()
    for e in entries:
        if not isinstance(e, dict):
            raise ValueError('entry must be an object')
        eid = slug(e.get('id'))
        if eid in ids:
            raise ValueError('duplicate entry ID: ' + eid)
        ids.add(eid)
        if e.get('kind') not in KINDS:
            raise ValueError('unknown entry kind')
        for field in ('title', 'group', 'stage', 'question', 'thesis', 'detail',
                      'evidence', 'edge', 'connection', 'next_step'):
            nonempty(e.get(field), eid + '.' + field)
        refs = e.get('source_ids')
        if not isinstance(refs, list) or any(not isinstance(r, str) or r not in source_ids for r in refs):
            raise ValueError('unknown or invalid source reference in ' + eid)
        if e['kind'] in ('case', 'article') and not refs:
            raise ValueError('case/article requires source references')
        sections = e.get('sections', [])
        if not isinstance(sections, list):
            raise ValueError('sections must be a list')
        if e['kind'] == 'article' and len(sections) < 3:
            raise ValueError('article requires at least three authored sections')
        for section in sections:
            if not isinstance(section, dict):
                raise ValueError('section must be an object')
            nonempty(section.get('heading'), 'section heading')
            nonempty(section.get('text'), 'section text')
            sr = section.get('source_ids', [])
            if not isinstance(sr, list) or any(not isinstance(r, str) or r not in refs for r in sr):
                raise ValueError('section references must belong to entry')
    for e in entries:
        links = e.get('related', [])
        if not isinstance(links, list) or any(not isinstance(r, str) or r not in ids for r in links):
            raise ValueError('unknown related entry')
    return data


def check(path):
    data = load_catalog(path)
    return {'catalog_hash': digest(data), 'entries': dict(Counter(e['kind'] for e in data['entries'])),
            'sources': len(data['sources']), 'validation': 'structure-only',
            'publication_approved': False}


STYLE = '''
:root{color-scheme:light;--ink:#252525;--muted:#595959;--accent:#993d25;--line:#ddd8d0;--paper:#fbfaf7}*{box-sizing:border-box}html{scroll-padding-top:24px}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.8 system-ui,-apple-system,"PingFang SC",sans-serif}a{color:var(--accent);text-underline-offset:3px}header,main,footer{max-width:1120px;margin:auto;padding:32px 28px}header{border-bottom:1px solid var(--line)}h1{font-size:clamp(28px,4vw,44px);line-height:1.3;max-width:850px;margin:8px 0 20px}h2{font-size:23px;line-height:1.5;margin:0}h3{font-size:20px;margin-top:30px}p{margin:12px 0}small,.meta{color:var(--muted);font-size:13px}.toolbar{display:flex;flex-wrap:wrap;gap:12px;align-items:end;margin:20px 0}label{display:block;font-size:14px}input,select,textarea,button{font:inherit;border:1px solid #9e9990;border-radius:4px;padding:8px 12px;background:white;color:var(--ink)}button{cursor:pointer}button:hover{background:#eee9df}input{width:min(100%,340px)}textarea{width:100%;min-height:90px;resize:vertical}input:focus-visible,select:focus-visible,textarea:focus-visible,button:focus-visible,summary:focus-visible,a:focus-visible{outline:3px solid #b95a39;outline-offset:3px}article{padding:26px 0;border-bottom:1px solid var(--line);scroll-margin-top:20px}.eyebrow{color:var(--accent);font-size:13px;letter-spacing:.04em}.thesis{font-size:18px;max-width:850px}details{margin:16px 0}summary{cursor:pointer;color:var(--accent);padding:6px 0}.dossier{display:grid;grid-template-columns:1fr 1fr;gap:4px 32px}.dossier strong{display:block;font-size:14px}.dossier p{font-size:15px}.reading{max-width:760px;margin:24px auto;padding:8px 0;font:18px/1.95 Georgia,"Songti SC",serif}.reading h3{font-family:system-ui,sans-serif}.references{font:14px/1.65 system-ui,sans-serif}.references li{margin:12px 0;overflow-wrap:anywhere}.review{padding:18px;background:#f1ede5;margin-top:20px}.review label{margin-bottom:8px}.review select{margin-bottom:10px}.notice{color:var(--muted);font-size:14px}.empty{padding:32px;border:1px solid var(--line)}[hidden]{display:none!important}@media(max-width:650px){header,main,footer{padding:24px 18px}.dossier{grid-template-columns:1fr}.toolbar>*{width:100%}.toolbar input,.toolbar select,.toolbar button{width:100%}.reading{font-size:17px}h2{font-size:21px}}@media print{.toolbar,.review,button{display:none}article{break-inside:avoid}details{display:block}body{background:white}}
'''

SCRIPT = r'''
const config=JSON.parse(document.getElementById('config').textContent);
const key='r2p-casebook:'+config.catalog_hash;
let decisions={};
const status=document.getElementById('save-status');
try{const saved=JSON.parse(localStorage.getItem(key)||'{}');if(saved && typeof saved==='object')decisions=saved;}catch(e){status.textContent='浏览器存储不可用；请在离开前导出反馈。';}
const rows=[...document.querySelectorAll('article[data-id]')];
function save(){try{localStorage.setItem(key,JSON.stringify(decisions));status.textContent='反馈已保存在此浏览器；请导出 JSON 交回管线。';}catch(e){status.textContent='保存失败；请立即导出反馈，刷新会丢失。';}}
function filter(){const q=document.getElementById('search').value.trim().toLocaleLowerCase();const kind=document.getElementById('kind').value;const group=document.getElementById('group').value;const decision=document.getElementById('decision-filter').value;let visible=0;rows.forEach(row=>{let d=decisions[row.dataset.id]?.decision||'pending';row.hidden=!((!kind||row.dataset.kind===kind)&&(!group||row.dataset.group===group)&&(!decision||decision===d)&&(!q||row.dataset.search.includes(q)));if(!row.hidden)visible++;});document.getElementById('count').textContent=`显示 ${visible} / ${rows.length} 项`;document.getElementById('empty').hidden=visible!==0;}
rows.forEach(row=>{let id=row.dataset.id;let select=row.querySelector('.choice'),note=row.querySelector('textarea');let d=decisions[id]||{};select.value=['pending','keep','revise','drop'].includes(d.decision)?d.decision:'pending';note.value=typeof d.comment==='string'?d.comment:'';function update(){decisions[id]={decision:select.value,comment:note.value};note.removeAttribute('aria-invalid');save();}select.addEventListener('change',update);note.addEventListener('input',update);});
['search','kind','group','decision-filter'].forEach(id=>document.getElementById(id).addEventListener('input',filter));
document.getElementById('export').addEventListener('click',()=>{const items=rows.map(row=>({id:row.dataset.id,...(decisions[row.dataset.id]||{decision:'pending',comment:''})}));const invalid=items.find(x=>['revise','drop'].includes(x.decision)&&!x.comment.trim());if(invalid){['search','kind','group','decision-filter'].forEach(i=>document.getElementById(i).value='');filter();const row=rows.find(r=>r.dataset.id===invalid.id);status.textContent='请为“'+row.querySelector('h2').textContent+'”补充修改或暂缓原因。';const note=row.querySelector('textarea');note.setAttribute('aria-invalid','true');note.setAttribute('aria-describedby','save-status');note.focus();row.scrollIntoView({block:'center'});return;}const blob=new Blob([JSON.stringify({schema_version:1,catalog_hash:config.catalog_hash,decisions:items},null,2)],{type:'application/json'});const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='editorial-feedback-'+config.catalog_hash.slice(0,12)+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);status.textContent='反馈文件已生成；尚未导入管线，也未批准发布。';});
function jump(){const id=decodeURIComponent(location.hash.slice(1));const row=rows.find(r=>r.id===id);if(row){['search','kind','group','decision-filter'].forEach(i=>document.getElementById(i).value='');filter();const d=row.querySelector('details');if(d)d.open=true;row.scrollIntoView();}}window.addEventListener('hashchange',jump);filter();jump();
'''


def build(path, target):
    data = load_catalog(path)
    target = Path(target)
    if target.exists():
        raise ValueError('review target already exists; choose a new revision')
    esc = html.escape
    sources = {s['id']: s for s in data['sources']}

    def refs(ids):
        return '<span class="references">' + ' · '.join(
            '<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>'.format(
                esc(sources[s]['url'], quote=True), esc(sources[s]['label'])) for s in ids) + '</span>'

    rows = []
    for e in data['entries']:
        eid = e['id']
        body = ''.join('<h3>{}</h3>{}{}'.format(esc(s['heading']),
                       ''.join('<p>' + esc(p) + '</p>' for p in s['text'].split('\n\n')),
                       refs(s.get('source_ids', []))) for s in e.get('sections', []))
        fields = [('question', '读者问题'), ('detail', '具体机制'), ('evidence', '已知依据'),
                  ('edge', '反例与缺口'), ('connection', '与你的研究如何相接'), ('next_step', '下一步')]
        dossier = ''.join('<div><strong>{}</strong><p>{}</p></div>'.format(label, esc(e[key])) for key, label in fields)
        evidence = '<ul class="references">' + ''.join('<li>{}<br>{} · 核对 {}</li>'.format(
            refs([s]), esc(sources[s]['note']), esc(sources[s]['checked_at'])) for s in e['source_ids']) + '</ul>'
        related = ' · '.join('<a href="#{}">{}</a>'.format(s, esc(next(x['title'] for x in data['entries'] if x['id'] == s))) for s in e.get('related', []))
        choices = ''.join('<option value="{}">{}</option>'.format(k, v) for k, v in DECISIONS.items())
        rows.append('''<article id="{id}" data-id="{id}" data-kind="{kind}" data-group="{group}" data-search="{search}">
<h2>{title}</h2><div class="meta">{label} / {group} / {stage} · {id}</div><p class="thesis">{thesis}</p>
<details><summary>{action}</summary><div class="reading">{body}</div><div class="dossier">{dossier}</div>{evidence}<p>{related}</p></details>
<div class="review"><label for="d-{id}">这项内容如何处理</label><select id="d-{id}" class="choice">{choices}</select><label for="n-{id}">你的修改意见</label><textarea id="n-{id}" placeholder="例如：保留案例，结论太宽；补一个反例。"></textarea></div></article>'''.format(
            id=eid, kind=e['kind'], group=esc(e['group'], quote=True), search=esc(json.dumps(e, ensure_ascii=False).lower(), quote=True),
            label=KINDS[e['kind']], stage=esc(e['stage']), title=esc(e['title']), thesis=esc(e['thesis']),
            action='展开文章全文与依据' if body else '展开案例机制与依据', body=body, dossier=dossier, evidence=evidence, related=related, choices=choices))
    kinds = ''.join('<option value="{}">{}</option>'.format(k, v) for k, v in KINDS.items() if any(e['kind'] == k for e in data['entries']))
    groups = ''.join('<option>{}</option>'.format(esc(g)) for g in dict.fromkeys(e['group'] for e in data['entries']))
    config = json.dumps({'catalog_hash': digest(data)}).replace('<', '\\u003c')
    page = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>{style}</style></head><body>
<header><h1>{title}</h1><p>{intro}</p><p class="notice">来源记录与文章判断分开。初核指已阅读产品说明，不代表实测、收入或效果验证。保留选题不等于批准发布。</p>
<div class="toolbar"><label>搜索案例、观点<input id="search" type="search" placeholder="输入项目名、机制或研究方向"></label><label>内容类型<select id="kind"><option value="">全部类型</option>{kinds}</select></label><label>研究方向<select id="group"><option value="">全部方向</option>{groups}</select></label><label>审阅状态<select id="decision-filter"><option value="">全部状态</option><option value="pending">待审</option><option value="keep">保留</option><option value="revise">修改</option><option value="drop">暂缓</option></select></label><button id="export">导出审阅反馈</button></div>
<p id="count" role="status"></p><p id="save-status" role="status" class="meta">反馈只保存在当前浏览器；导出 JSON 后可交回管线。没有自动上传。</p></header>
<main><p id="empty" class="empty" hidden>没有匹配项。请缩短搜索词或切换筛选。</p>{rows}</main><footer>本页是私有编辑工作台。校验只检查结构、引用关联和反馈版本，不评定文章质量，也不验证网页声明。</footer>
<script type="application/json" id="config">{config}</script><script>{script}</script></body></html>'''.format(
        title=esc(data['title']), intro=esc(data['intro']), style=STYLE, kinds=kinds, groups=groups, rows=''.join(rows), config=config, script=SCRIPT)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('x', encoding='utf-8') as handle:
        handle.write(page)
    return {'path': str(target.resolve()), **check(path)}


def import_feedback(catalog_path, feedback_path, target):
    data = load_catalog(catalog_path)
    review = read_json(feedback_path)
    if not isinstance(review, dict) or review.get('schema_version') != 1 or review.get('catalog_hash') != digest(data):
        raise ValueError('feedback is invalid or belongs to a different catalog revision')
    decisions = review.get('decisions')
    if not isinstance(decisions, list) or not decisions:
        raise ValueError('feedback decisions must be a non-empty list')
    valid = {e['id'] for e in data['entries']}
    seen = set()
    for item in decisions:
        if not isinstance(item, dict) or not isinstance(item.get('id'), str) or item['id'] not in valid or item['id'] in seen:
            raise ValueError('unknown or duplicate feedback entry')
        seen.add(item['id'])
        if item.get('decision') not in DECISIONS or not isinstance(item.get('comment'), str):
            raise ValueError('invalid feedback decision/comment')
        if item['decision'] in ('revise', 'drop'):
            nonempty(item['comment'], 'revision or deferral reason')
    target = Path(target)
    if target.exists():
        raise ValueError('feedback target already exists')
    result = {'schema_version': 1, 'catalog_hash': digest(data), 'publication_approved': False,
              'decisions': [{'id': i['id'], 'decision': i['decision'], 'comment': i['comment']} for i in decisions]}
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('x', encoding='utf-8') as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
    return {'path': str(target.resolve()), 'decisions': len(decisions), 'publication_approved': False}
