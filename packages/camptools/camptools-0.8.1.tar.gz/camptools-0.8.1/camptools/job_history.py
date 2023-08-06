from .jobs import JobHistoryManager
from argparse import ArgumentParser


def parse_args():
    parser = ArgumentParser()

    parser.add_argument('--correct_date', '-cd', action='store_true')
    parser.add_argument('--nshow', '-n', type=int, default=-1)

    return parser.parse_args()


def job_history():
    args = parse_args()

    job_dict = JobHistoryManager()
    job_dict.load()

    if args.correct_date:
        job_dict.correct_date()
        job_dict.save()

    jobs = list(job_dict.dict.values())
    jobs_show = jobs[:args.nshow]

    for job in jobs_show:
        print(job)
