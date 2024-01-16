import hashlib

from ..config import get_config



config = get_config()

def enumerate_at(collection, start):
    return enumerate(collection[start:], start)

def find_subclasses(cls: type):
    """ Recursively searches for every direct and indirect subclass of `cls` """
    
    def _find(cls, classes):
        for subcls in cls.__subclasses__():
            classes.append(subcls)
            _find(subcls, classes)
    
    classes = []
    _find(cls, classes)
    
    return classes


def get_hash(*data: any, truncate=0):
    data_str = ''.join(str(s) for s in data)
    hash = hashlib.sha1(data_str.encode("utf-8")).hexdigest()
    end = truncate or len(hash)
    return hash[:end]


def leading_whitespaces(string: str):
    string = string.replace("\t", " " * config.mdparser.tabsize)
    return len(string) - len(string.lstrip(' '))



def multiline_strip(lines):

    while lines:
        if lines[0].strip() == "":
            del lines[0]
        else:
            break
    
    while lines:
        if lines[-1].strip() == "":
            del lines[-1]
        else:
            break

    return lines


def find_line(lines, start, function, negate=False):
    end = len(lines)
    for i, line in enumerate(lines[start:], start):
        if (not negate and function(line)) or (negate and not function(line)):
            end = i
            break
    return end


