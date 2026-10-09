import argparse
import json
import sys
from .core import Workspace


def main():
    p = argparse.ArgumentParser(description='Research → reviewed site article → platform-native social package')
    p.add_argument('--workspace', required=True, help='Private data directory, outside the public code repository')
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('init')
    sub.add_parser('sync').add_argument('--config', required=True)
    ingest = sub.add_parser('ingest')
    ingest.add_argument('id')
    group = ingest.add_mutually_exclusive_group(required=True)
    group.add_argument('--file')
    group.add_argument('--github', metavar='OWNER/REPO')
    ingest.add_argument('--ref', help='Full commit SHA')
    ingest.add_argument('--path', help='Repository-relative file path')
    ingest.add_argument('--chatgpt', action='store_true')
    ingest.add_argument('--conversation-id')
    ingest.add_argument('--public-url')
    topic = sub.add_parser('topic')
    topic.add_argument('id')
    topic.add_argument('--title', required=True)
    topic.add_argument('--question', required=True)
    topic.add_argument('--sources', nargs='+', required=True)
    topic.add_argument('--channels', nargs='+', choices=['site', 'wechat', 'xiaohongshu'])
    route = sub.add_parser('route')
    route.add_argument('id')
    route.add_argument('--channels', nargs='+', required=True, choices=['site', 'wechat', 'xiaohongshu'])
    route.add_argument('--reason', required=True)
    feedback = sub.add_parser('feedback-add')
    feedback.add_argument('--file', required=True)
    resolve = sub.add_parser('feedback-resolve')
    resolve.add_argument('id')
    resolve.add_argument('--decision', required=True, choices=['revised', 'no-change'])
    resolve.add_argument('--note', required=True)
    impact = sub.add_parser('impact')
    impact.add_argument('--source')
    for command in ('brief', 'validate', 'build', 'status'):
        sub.add_parser(command).add_argument('id')
    review = sub.add_parser('review')
    review.add_argument('id')
    review.add_argument('--reviewer', required=True)
    review.add_argument('--note', required=True)
    export = sub.add_parser('export')
    export.add_argument('id')
    export.add_argument('--to', required=True)
    export.add_argument('--site-repo')
    png = sub.add_parser('rasterize')
    png.add_argument('--package', required=True)
    png.add_argument('--to', required=True)
    png.add_argument('--font', required=True)
    record = sub.add_parser('record')
    record.add_argument('id')
    record.add_argument('--channel', choices=['site', 'wechat', 'xiaohongshu'], required=True)
    record.add_argument('--url', required=True)
    record.add_argument('--note', required=True)
    args = p.parse_args()
    w = Workspace(args.workspace)
    try:
        if args.command in ('route', 'feedback-add', 'feedback-resolve', 'impact'):
            from .feedback import add, resolve, impact, route
            if args.command == 'route':
                result = route(w, args.id, args.channels, args.reason)
            elif args.command == 'feedback-add':
                result = add(w, args.file)
            elif args.command == 'feedback-resolve':
                result = resolve(w, args.id, args.decision, args.note)
            else:
                result = impact(w, args.source)
        elif args.command == 'init':
            result = w.init()
        elif args.command == 'rasterize':
            from .cards import rasterize
            result = rasterize(args.package, args.to, args.font)
        elif args.command == 'sync':
            result = w.sync(args.config)
        elif args.command == 'ingest':
            if args.chatgpt and not args.file:
                raise ValueError('--chatgpt requires --file')
            result = w.ingest(args.id, path=args.file, repo=args.github, ref=args.ref,
                              github_path=args.path, chatgpt=args.chatgpt,
                              conversation_id=args.conversation_id, public=args.public_url)
        elif args.command == 'topic':
            result = w.create_topic(args.id, args.title, args.question, args.sources, args.channels)
        elif args.command == 'review':
            result = w.review(args.id, args.reviewer, args.note)
        elif args.command == 'export':
            result = w.export(args.id, args.to, args.site_repo)
        elif args.command == 'record':
            result = w.record(args.id, args.channel, args.url, args.note)
        else:
            result = getattr(w, args.command)(args.id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError, TypeError) as error:
        print('Error: ' + str(error), file=sys.stderr)
        sys.exit(2)
