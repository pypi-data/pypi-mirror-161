import datetime
import os
import subprocess
from argparse import ArgumentParser
from pathlib import Path

import f90nml

from .jobs import JobHistoryManager

save_file = Path().home() / 'jobs.txt'


def calc_procs(filename):
    nml = f90nml.read(filename)
    nodes_str = nml['mpi']['nodes']
    nodes = list(map(int, nodes_str))
    return nodes[0] * nodes[1] * nodes[2]


def create_emjob(inputfile, jobfile, outputfile):
    procs = calc_procs(inputfile)
    nodes = procs // 64

    with open(jobfile, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.startswith('#QSUB -A'):
            lines[i] = '#QSUB -A p={}:t=1:c=64:m=90G\n'.format(nodes)
        elif line.startswith('aprun') and 'mpiemses3D' in line:
            lines[i] = 'aprun -n {} -d 1 -N 64 ./mpiemses3D plasma.inp\n'.format(
                procs)

    with open(outputfile, 'w', encoding='utf-8') as f:
        f.writelines(lines)


def qsub(filename):
    # execute 'qsub <job-file>'
    res = subprocess.Popen(
        ['qsub', filename],
        stdout=subprocess.PIPE)

    # byte to str and show
    res_str = [line.decode('utf-8') for line in res.stdout.readlines()][:1]
    print(''.join(res_str))

    # extracte job_id from response
    job_id = int(res_str[0]
                 .replace('.ja', '')
                 .replace('.jb', '')
                 .replace('.jc', '')
                 .strip())
    return job_id


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('jobfile')
    parser.add_argument('--inputfile', '-i', default='plasma.inp')
    parser.add_argument('--output', '-o', default='myjob.sh')
    parser.add_argument('--message', '-m', default='')
    parser.add_argument('--date', action='store_true')
    parser.add_argument('--directory', '-d', default=None)
    return parser.parse_args()


def nmyqsub():
    args = parse_args()

    if args.directory is not None:
        os.chdir(args.directory)

    jobfile = args.jobfile

    job_id = qsub(jobfile)

    date = ''
    if args.date:
        date = str(datetime.datetime.now())

    JobHistoryManager().save_job(job_id, Path('.').resolve(), args.message, date)


def myqsub():
    args = parse_args()

    if args.directory is not None:
        os.chdir(args.directory)

    jobfile = args.jobfile
    create_emjob(args.inputfile, args.jobfile, args.output)
    jobfile = args.output

    job_id = qsub(jobfile)

    date = ''
    if args.date:
        date = str(datetime.datetime.now())

    JobHistoryManager().save_job(job_id, Path('.').resolve(), args.message, date)
