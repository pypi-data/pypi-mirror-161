import json
import sys


def get_cookies() -> str:
    try:
        return json.loads(sys.argv[1])['cookies']
    except (IndexError, KeyError):
        return ''


def get_run_token() -> str:
    li = get_cookies().split('; ')
    for it in li:
        k, v = it.split('=')
        if 'run' in k and 'token' in k:
            return v
    return ''

