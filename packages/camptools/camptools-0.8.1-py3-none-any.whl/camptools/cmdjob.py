from argparse import ArgumentParser
from pathlib import Path

from .settings import Settings

job_template = '''#!/bin/bash
#============ PBS Options ============
#QSUB -ug {usergroup}
#QSUB -q {usergroup}{system}
#QSUB -r n
#QSUB -W {walltime}
#QSUB -A p=1:t=1:c=1:m={memory}

#============ Shell Script ============
set -x

{executor}{command}
'''


EXECUTORS = {
    'a': 'aprun -n 1 ',
    'b': '',
    'c': ''
}


def register_settings(args):
    if args.local:
        settings = Settings()
    else:
        try:
            settings = Settings.load()
        except Exception:
            settings = Settings.home()
    print(f'settings -> {settings._filepath.resolve()}')

    if 'jobcmd' not in settings:
        settings['jobcmd'] = {}

    if args.usergroup is not None:
        settings['jobcmd']['usergroup'] = args.usergroup
    if args.system is not None:
        settings['jobcmd']['system'] = args.system

    if args.walltime is not None:
        settings['jobcmd']['walltime'] = args.walltime
    elif 'walltime' not in settings['jobcmd']:
        settings['jobcmd']['walltime'] = '128:00'

    if args.memory is not None:
        settings['jobcmd']['memory'] = args.memory
    elif 'memory' not in settings['jobcmd']:
        settings['jobcmd']['memory'] = '90G'

    settings.save()


def create_job(args):
    settings = Settings.load()
    if args.verbose:
        print(f'used settings -> {settings._filepath.resolve()}')

    usergroup = settings['jobcmd']['usergroup']
    system = settings['jobcmd']['system']
    executor = EXECUTORS[system]
    walltime = settings['jobcmd']['walltime']
    memory = settings['jobcmd']['memory']
    command = args.command
    job_text = job_template.format(
        usergroup=usergroup,
        system=system,
        executor=executor,
        walltime=walltime,
        memory=memory,
        command=command,
    )

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(job_text)


def parse_args():
    parser = ArgumentParser()

    subparsers = parser.add_subparsers()

    parser_register = subparsers.add_parser('register')
    parser_register.add_argument('--usergroup', '-ug', default=None)
    parser_register.add_argument('--system', '-s', default='a',
                                 choices=['a', 'b', 'c'])
    parser_register.add_argument('--local', action='store_true')
    parser_register.add_argument('--walltime', '-w', default=None)
    parser_register.add_argument('--memory', '-m', default=None)
    parser_register.set_defaults(handler=register_settings)

    parser_create = subparsers.add_parser('create')
    parser_create.add_argument('command')
    parser_create.add_argument('--verbose', '-v', action='store_true')
    parser_create.add_argument('--output', '-o', default='tmpjob.sh')
    parser_create.set_defaults(handler=create_job)

    return parser.parse_args()


def cmdjob():
    args = parse_args()

    args.handler(args)
