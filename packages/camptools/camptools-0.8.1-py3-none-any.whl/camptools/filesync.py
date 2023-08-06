from time import sleep
from argparse import ArgumentParser
from .settings import Settings


FILE_SYNC_KEY = 'FILESYNC'


def lock(args):
    settings = Settings.home()

    settings[FILE_SYNC_KEY][args.key] = 'lock'

    settings.save()


def wait(args):
    for _ in range(args.max_wait):
        settings = Settings.home()
        if args.key not in settings[FILE_SYNC_KEY] \
                or settings[FILE_SYNC_KEY][args.key] != 'lock':
            break
        sleep(args.interval)
    else:
        print('[Error] Maximum waiting time exceeded')
        exit(1)


def notify(args):
    settings = Settings.home()

    del settings[FILE_SYNC_KEY][args.key]

    settings.save()


def main():
    settings = Settings.home()
    if FILE_SYNC_KEY not in settings:
        settings[FILE_SYNC_KEY] = {}
        settings.save()

    parser = ArgumentParser()

    sub_parsers = parser.add_subparsers()

    parser_lock = sub_parsers.add_parser('lock')
    parser_lock.add_argument('key')
    parser_lock.set_defaults(handler=lock)

    parser_wait = sub_parsers.add_parser('wait')
    parser_wait.add_argument('key')
    parser_wait.add_argument('--max_wait', type=int, default=10000)
    parser_wait.add_argument('-i', '--interval', type=int, default=5)
    parser_wait.set_defaults(handler=wait)

    parser_notify = sub_parsers.add_parser('notify')
    parser_notify.add_argument('key')
    parser_notify.set_defaults(handler=notify)

    args = parser.parse_args()

    if hasattr(args, 'handler'):
        args.handler(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
