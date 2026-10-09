"""Run without installation: python3 examples/demo.py --workspace /tmp/r2p-demo."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from research_to_publish.core import Workspace, write_json


def populate(w):
    w.init()
    w.ingest('demo-source', path=Path(__file__).with_name('source.md'))
    w.ingest('demo-chat', path=Path(__file__).with_name('chatgpt-capture.json'), chatgpt=True)
    tid = 'one-research-three-readers'
    if not (w.root / 'topics' / tid).exists():
        w.create_topic(tid, '一份研究，三种阅读需要', '怎样复用研究而不复制稿件？', ['demo-source', 'demo-chat'])
    topic, _ = w.load(tid)
    topic['claims'] = [{'id': 'different-readers', 'kind': 'interpretation',
        'text': '研究证据可以复用，平台表达应按读者需求重写。',
        'boundary': '这是编辑方法建议，不是增长实验结论。',
        'evidence': [{'source': 'demo-source', 'quote': '网站保留完整证据，公众号展开专业判断，小红书解释具体问题。'},
                     {'source': 'demo-chat', 'quote': '先整理证据，再根据读者需求分别写作。'}]}]
    def section(heading, body):
        return {'heading': heading, 'body': body, 'claims': ['different-readers']}
    editorial = {
      'site': {'title': '一份研究怎样形成三个平台的文章', 'summary': '用一个合成示例说明证据复用和平台写作的区别。', 'date': '2026-10-09',
               'sections': [section('证据与表达分开维护', '研究材料回答事实从哪里来。文章则需要根据读者的问题重新组织。网站保留完整推理，方便后续修订。'),
                            section('边界与后续验证', '本例只演示工程流程，不能证明这种写法提升传播。真实发布后仍需检查读者是否理解、是否愿意继续阅读。')]},
      'wechat': {'title': '内容复用时，哪些东西值得保持一致？', 'summary': '相同事实可以支撑不同文章，但每篇都应有自己的论证。',
                 'sections': [section('保持一致的是证据', '专业读者需要知道结论基于什么，以及何时不再成立。复用来源时应同时带上限制条件。'),
                              section('重新组织的是论证', '公众号从一个专业问题展开，让案例和反例推动结论。网站上的全部资料不必逐段搬来。')]},
      'xiaohongshu': {'title': '一份研究怎么写三篇？', 'caption': '先想清楚读者来找什么答案。下面是一个合成演示，不是涨粉秘籍。',
                      'cards': [section('先留住证据', '把来源和结论连在一起。\n改写之前，先知道哪句话能被证据支持。'),
                                section('每篇换一个问题', '网站：依据是什么？\n公众号：该怎么判断？\n小红书：这和我有什么关系？'),
                                section('更新要找得到原稿', '事实变了，顺着来源关系找到受影响的稿件，再决定如何修订。')]}}
    write_json(w.root / 'topics' / tid / 'topic.json', topic)
    write_json(w.root / 'topics' / tid / 'editorial.json', editorial)
    return tid


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--workspace', required=True)
    args = p.parse_args()
    w = Workspace(args.workspace)
    tid = populate(w)
    w.brief(tid)
    print(json.dumps(w.build(tid), ensure_ascii=False, indent=2))
