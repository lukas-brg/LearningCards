import hashlib
import re
from collections import defaultdict
from itertools import dropwhile

from ..config import get_config


config = get_config()


def sanitize_string(string):
    string = string.strip().lower()
    string = re.sub(r"[^a-z0-9\s]", "", string)
    string = re.sub(r"\s+", "-", string)
    return string


def find_subclasses(cls: type) -> list[type]:
    """ Recursively searches for every direct and indirect subclass of `cls` """
    def _find(cls):
        for subcls in cls.__subclasses__():
            yield subcls
            yield from _find(subcls)

    return list(_find(cls))


__hashes = defaultdict(int)


def make_id_hash(*data: any, limit_len=None, ensure_unique=True) -> str:

    data_str = ''.join(str(d) for d in data)
    hash = hashlib.sha256(data_str.encode("utf-8")).hexdigest()
    len_hash = len(hash)
    end = limit_len or len_hash
    end = min(end, len_hash)
    hash = hash[:end]

    if not ensure_unique:
        return hash

    counter = __hashes[hash]
    unique_hash = hash if counter == 0 else f"{hash}{counter}"
    __hashes[hash] += 1
    return unique_hash


def leading_whitespaces(string: str):
    string = string.replace("\t", " " * config.mdparser.tabsize)
    return len(string) - len(string.lstrip(' '))


def multiline_strip(lines: list[str]) -> list[str]:
    lines = list(dropwhile(lambda line: line.strip() == "", lines))
    lines.reverse()
    lines = list(dropwhile(lambda line: line.strip() == "", lines))
    lines.reverse()
    return lines


def find_line(lines, start, function, negate=False):
    end = len(lines)
    for i, line in enumerate(lines[start:], start):
        if (not negate and function(line)) or (negate and not function(line)):
            end = i
            break
    return end
