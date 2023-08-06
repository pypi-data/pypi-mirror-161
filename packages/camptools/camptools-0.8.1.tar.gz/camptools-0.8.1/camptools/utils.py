import os
import shutil as sh
import subprocess
from pathlib import Path


def call(cmd, encoding='utf-8'):
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    o_data, e_data = p.communicate()
    return o_data.decode(encoding), e_data.decode(encoding)


def copy(from_file: Path, to_file: Path):
    if from_file.exists():
        sh.copy(str(from_file), str(to_file))
    else:
        print('{} is not found'.format(from_file))


def symlinkfile(from_path: Path, to_path: Path):
    os.symlink(from_path, to_path, target_is_directory=False)


def symlinkdir(from_path: Path, to_path: Path):
    os.symlink(from_path, to_path, target_is_directory=True)
