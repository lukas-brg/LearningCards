import hashlib, re

from itertools import dropwhile, takewhile

from ..config import get_config



config = get_config()

def clean_string(string):
    return re.sub(r'[^a-zA-Z0-9]', '', string).lower()



def find_subclasses(cls: type):
    """ Recursively searches for every direct and indirect subclass of `cls` """
    
    def _find(cls, classes):
        for subcls in cls.__subclasses__():
            classes.append(subcls)
            _find(subcls, classes)
    
    classes = []
    _find(cls, classes)
    
    return classes


def get_hash(*data: any, max_length=None) -> str:
    data_str = ''.join(str(d) for d in data)
    hash = hashlib.sha256(data_str.encode("utf-8")).hexdigest()
    len_hash = len(hash)
    end = max_length or len_hash
    end = min(end, len_hash)
    
    return hash[:end]


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


    