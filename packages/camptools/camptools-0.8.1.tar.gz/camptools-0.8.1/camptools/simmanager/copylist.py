import json
from os import PathLike
from pathlib import Path
from typing import List


def search_copylist(filename: PathLike, key: str) -> List[Path]:
    with open(filename, 'r', encoding='utf-8') as f:
        jsonobj = json.load(f)

    if key in jsonobj:
        copylist = []
        for filename in jsonobj[key]:
            copylist.append(Path(filename))

        return copylist
    else:
        raise KeyError('key ({}) is not exists'.format(key))
