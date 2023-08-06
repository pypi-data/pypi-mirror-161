from argparse import ArgumentParser
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .settings import Settings


CHECKPOINTS_KEY = 'checkpoints'


@dataclass
class Checkpoint:
    path: str
    message: str
    time: str

    def todict(self):
        return {
            'path': self.path,
            'message': self.message,
            'time': self.time,
        }

    @classmethod
    def fromdict(self, dic):
        path = dic['path']
        message = dic['message']
        time = dic['time']
        return Checkpoint(path, message, time)


def parse_args():
    parser = ArgumentParser()

    subparsers = parser.add_subparsers()
    parser.add_argument('--message', '-m', default=None)

    parser_register = subparsers.add_parser(
        'register', description='Register checkpoint')
    parser_register.set_defaults(handler=register)

    parser_clean = subparsers.add_parser(
        'clear', description='Clean checkpoints')
    parser_clean.add_argument('--all', '-a', action='store_true')
    parser_clean.add_argument('--index', '-i', type=int, default=None)
    parser_clean.set_defaults(handler=clear)

    parser_list = subparsers.add_parser('list', description='Show checkpoints')
    parser_list.set_defaults(handler=show_list)

    args = parser.parse_args()

    if hasattr(args, 'handler'):
        args.handler(args)
    else:
        register(args)


def register(args):
    settings = Settings.home()
    if CHECKPOINTS_KEY not in settings:
        settings[CHECKPOINTS_KEY] = []

    curdir_str = str(Path().resolve())

    for cp_dic in settings[CHECKPOINTS_KEY]:
        checkpoint = Checkpoint.fromdict(cp_dic)
        if curdir_str == checkpoint.path:
            settings[CHECKPOINTS_KEY].remove(cp_dic)
            break

    time = str(datetime.now())
    checkpoint = Checkpoint(curdir_str, str(args.message), time)

    settings[CHECKPOINTS_KEY].append(checkpoint.todict())

    settings.save()


def clear(args):
    settings = Settings.home()
    if CHECKPOINTS_KEY not in settings:
        settings[CHECKPOINTS_KEY] = []

    if args.all:
        settings[CHECKPOINTS_KEY] = []
    elif args.index is not None:
        if 0 <= args.index and args.index < len(settings[CHECKPOINTS_KEY]):
            del settings[CHECKPOINTS_KEY][args.index]
    settings.save()


def show_list(args):
    settings = Settings.home()
    if CHECKPOINTS_KEY not in settings:
        settings[CHECKPOINTS_KEY] = []

    for i, cp_dic in enumerate(settings[CHECKPOINTS_KEY]):
        checkpoint = Checkpoint.fromdict(cp_dic)
        path = checkpoint.path
        message = checkpoint.message
        time = checkpoint.time
        print(f'[{i}] {path} : {message} : {time}')


def main():
    parse_args()


if __name__ == '__main__':
    main()
