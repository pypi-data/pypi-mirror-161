import json
from pathlib import Path
from typing import Any

SETTINGS_FILENAME = '.camptools'


class Settings:
    MAX_DEPTH: int = 50

    def __init__(self, filepath: Path = None):
        filepath = filepath or (Path() / SETTINGS_FILENAME)
        self._filepath: Path = filepath

        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                self._jsonobj: dict = json.load(f)
        else:
            self._jsonobj: dict = {}
    
    @classmethod
    def home(cls) -> "Settings":
        return Settings(Path.home() / SETTINGS_FILENAME)

    @classmethod
    def load(cls) -> "Settings":
        # 現在のディレクトリから一番近い設定ファイルを探索する
        curdir = Path().resolve()
        while not (curdir / SETTINGS_FILENAME).exists():
            # 一番上まで探索したら終了
            if curdir == curdir.parent:
                break

            curdir = curdir.parent

        if not (curdir / SETTINGS_FILENAME).exists():
            raise Exception('[Error] settings file(.camptools) is not found.')
        filepath = curdir / SETTINGS_FILENAME
        return Settings(filepath)

    def save(self, filepath: Path = None):
        if filepath is None:
            filepath = self._filepath

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self._jsonobj, f)

    def __getitem__(self, key: str) -> Any:
        return self._jsonobj[key]

    def __setitem__(self, key: str, value: Any):
        self._jsonobj[key] = value

    def __contains__(self, key):
        return key in self._jsonobj

    @property
    def filepath(self):
        return self._filepath
