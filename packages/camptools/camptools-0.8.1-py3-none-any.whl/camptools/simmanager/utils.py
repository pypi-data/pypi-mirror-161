import json
from argparse import ArgumentParser, Namespace
from copy import deepcopy
from os import PathLike
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

import emout
from emout.utils import InpFile
from f90nml import Namelist

from ..utils import call, copy, symlinkdir
from .copylist import search_copylist
from .utils import *

COPYLIST = Path().home() / 'copylist.json'


def latest_directory_index(base_directory_name: str) -> int:
    index = 1
    new_directory = Path(f'{base_directory_name}_{index}')
    while new_directory.exists():
        index += 1
        new_directory = Path(f'{base_directory_name}_{index}')

    return index - 1


def copy_inpFile(inp: InpFile) -> InpFile:
    inp_copy = InpFile()
    inp_copy.nml = deepcopy(inp.nml)
    inp_copy.convkey = deepcopy(inp.convkey)

    return inp_copy


def fork_inpFile(inp: InpFile, nstep: Union[int, None] = None, params: Dict[Tuple[Any], Any] = {}):
    inp = copy_inpFile(inp)

    if nstep:
        inp.nstep = nstep

    for keys, value in params.items():
        if not isinstance(keys, Tuple):
            keys = tuple(keys)

        cur = inp
        for key in keys[:-1]:
            cur = cur[key]
        cur[keys[-1]] = value

    return inp


def create_inpFile(*inpFiles: List[InpFile]) -> InpFile:
    if len(inpFiles) > 0:
        base_inp = copy_inpFile(inpFiles[0])

        for inpfile in inpFiles[1:]:
            for group in inpfile.nml.keys():
                for key in inpfile.nml[group].keys():
                    value = inpfile.nml[group][key]

                    if key in inpfile.nml[group].start_index:
                        start_index = inpfile.nml[group].start_index[key][0]
                        value = list(value)
                        base_inp.setlist(group, key, value,
                                        start_index=start_index)
                    else:
                        if group not in base_inp.nml:
                            base_inp.nml[group] = Namelist()
                        base_inp.nml[group][key] = value
    return base_inp


def create_directory(to_dir: Path, key: str):
    directory: Path = Path('.') / to_dir
    directory.mkdir(exist_ok=True)

    copylist = search_copylist(COPYLIST, key)

    for filepath in copylist:
        name = filepath.name
        copy(filepath, directory / name)
