import json
import os.path
import sys
from .__init__ import NotXueersiError


def get_cookies() -> str:
    try:
        return json.loads(sys.argv[1])['cookies']
    except (IndexError, KeyError):
        raise NotXueersiError()
        # return 'not_xes = true;'


def get_run_token() -> str:
    li = get_cookies().split('; ')
    for it in li:
        k, v = it.split('=')
        if 'run' in k and 'token' in k:
            return v
    return ''


def get_pid() -> int:
    pid = os.path.split(
        os.path.split(
            sys.argv[0]
        ).__getitem__(0)
    ).__getitem__(1)
    try:
        return int(pid)
    except ValueError:
        raise NotXueersiError()
