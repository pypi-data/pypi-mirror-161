import os


def init():
    if not os.path.exists('.git'):
        os.system('git init')


def add(s: str):
    os.system(f'git add {s}')


def push(s: str):
    os.system(f'git push {s}')


def remote(s: str):
    os.system(f'git remote {s}')


def pull(s: str):
    os.system(f'git pull {s}')


def commit(s: str):
    os.system(f'git commit -m "{s}"')


def _args(s: str):
    os.system(f'git {s}')


