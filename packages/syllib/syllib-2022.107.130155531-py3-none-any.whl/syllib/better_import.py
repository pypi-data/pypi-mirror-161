import os
import sys


def abs_import(path: str, _globals=None, _locals=None, fromlist=(), level=0):
    dirname, basename = os.path.split(path)
    sys.path.append(dirname)
    module = __import__(
        name=basename,
        globals=_globals,
        locals=_locals,
        fromlist=fromlist,
        level=level
    )
    sys.path.pop()
    return module
