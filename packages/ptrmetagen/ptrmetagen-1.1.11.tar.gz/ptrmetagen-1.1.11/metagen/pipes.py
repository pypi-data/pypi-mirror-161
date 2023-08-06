from metagen.helpers import Pipe, is_exist, str2Path


class PathCheck(Pipe):
    """helper class provided converting str input to Path and check if path exist"""
    str2Path = str2Path
    is_exist = is_exist

path_check = PathCheck()