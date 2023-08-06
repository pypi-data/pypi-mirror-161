from pathlib import Path
from collections import OrderedDict
from .utils import call

import typing
from typing import List


class Singleton(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance


class JobHistoryData:
    """Job history data.
    """

    def __init__(self,
                 job_id: int,
                 directory: str,
                 message: str = '',
                 date: str = ''):
        self.job_id = job_id
        self.directory = directory
        self.message = message
        self.date = date

    @classmethod
    def loads(cls, line: str) -> 'JobHistoryData':
        splited = line.split(',')
        if len(splited) != 4:
            return None
        job_id = int(splited[0].strip())
        directory = splited[1].strip()
        message = splited[2].strip()
        date = splited[3].strip()
        return JobHistoryData(job_id, directory, message, date)

    def correct_date(self, force: bool = False):
        if not force and len(self.date) > 0:
            return

        path = Path(self.directory)
        output_files = list(path.glob('*.o{}'.format(self.job_id)))
        if len(output_files) == 0:
            self.date = 'None'
            return

        output_file = output_files[0]
        o_data, _ = call('tail {} -n 30'.format(output_file.resolve()))
        lines = o_data.splitlines()
        for line in lines:
            if 'Resource Usage on' in line:
                self.date = line.replace('Resource Usage on', '').strip()
                break
        else:
            self.date = self.date or 'None'

    def __str__(self) -> str:
        return '{}, {}, {}, {}'.format(
            self.job_id,
            self.directory,
            self.message,
            self.date,
        )


class JobHistoryManager(Singleton):
    """Class to manage job history.
    """

    def __init__(self):
        self.save_file = Path().home() / 'jobs.txt'
        self.save_file.touch(exist_ok=True)
        self.dict: typing.OrderedDict[int, JobHistoryData] = None

    def save_job(self,
                 job_id: str or int,
                 directory: str,
                 message: str = '',
                 date: str = ''):
        job = JobHistoryData(job_id, directory, message, date)
        with open(str(self.save_file), 'a', encoding='utf-8') as f:
            f.write('{}\n'.format(job))

    def load(self):
        self.dict = OrderedDict()
        with open(str(self.save_file), 'r', encoding='utf-8') as f:
            for line in f:
                job = JobHistoryData.loads(line)
                if job is not None:
                    self.dict[job.job_id] = job

    def correct_date(self, force=False):
        for job in self.dict.values():
            job.correct_date(force=force)

    def save(self):
        with open(str(self.save_file), 'w', encoding='utf-8') as f:
            for job in self.dict.values():
                f.write('{}\n'.format(job))

    def __iter__(self):
        return iter(self.dict)

    def __getitem__(self, job_id: int) -> JobHistoryData:
        return self.dict[job_id]


class SubmitedJobInfo:
    def __init__(self, tokens, source='o', encoding='utf-8'):
        self.queue = tokens[0]
        self.user = tokens[1]
        self.jobid = int(tokens[2])
        self.status = tokens[3]
        self.proc = int(tokens[4])
        self.thread = int(tokens[5])
        self.core = int(tokens[6])
        self.memory = int(tokens[7].replace('G', '').replace('M', ''))
        self.elapse = tokens[8]

        self.source = source

        self.encoding = encoding

    def tail(self, ntail=5) -> str:
        o_data, _ = call(f'qcat -{self.source} {self.jobid} | tail -n {ntail}',
                         encoding=self.encoding)
        return o_data


def create_submited_jobs(source='o') -> List[SubmitedJobInfo]:
    o_data, e_data = call('qs', encoding='utf-8')
    lines = o_data.split('\n')
    jobs = []
    for line in lines[1:-1]:
        tokens = line.strip().split()
        jobs.append(SubmitedJobInfo(tokens, source=source))
    return jobs
