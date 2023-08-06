import os
import json
from glob import glob
from typing import Union, Tuple, List, Any
import os
from glob import glob
from typing import List

_denominators = {"GB": 1024 ** 3, "MB": 1024 ** 2, "KB": 1024 ** 1, "Bytes": 1024 ** 0}


def load_json(path: str, encoding: str = 'utf-8') -> Union[Tuple, List]:
    with open(path, encoding=encoding) as r:
        return json.load(r)


def write_json(path: str, content: Any, encoding: str = "utf-8") -> None:
    with open(path, 'w', encoding=encoding) as w:
        json.dump(content, w)


def get_all_path(dir_path: str, ext: str = ".*") -> List[str]:
    return glob(os.path.join(dir_path, "**/*" + ext), recursive=True)


def get_total_size(paths: List[str], metric: str = "GB") -> int:
    if metric in _denominators:
        return sum(
            [os.path.getsize(path) / _denominators[metric]
             for path in paths if os.path.isfile(path)]
        )
    raise KeyError("Enter the metric one of 'GB','MB','KB', and 'Bytes'.")


def chk_dir_and_mkdir(fullpath: str) -> None:
    dirs = [fullpath]
    while True:
        directory = os.path.dirname(dirs[0]) if not os.path.isdir(dirs[0]) else dirs[0]
        if directory == dirs[0] or not directory:
            break
        if directory:
            dirs.insert(0, directory)
    for dir in dirs[:-1]:
        if not os.path.isdir(dir):
            os.mkdir(dir)
        # sss
