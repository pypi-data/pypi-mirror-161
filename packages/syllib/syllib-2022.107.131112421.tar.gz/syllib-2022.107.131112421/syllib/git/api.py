from .git import init, remote, pull, add, push


def upload(username: str, repository: str, files: list, branch: str = 'main'):
    url = f'https://github.com/{username}/{repository}.git'
    init()
    remote(f'add _uploading {url}')
    # pull(f'_uploading {branch}:master')
    for f in files:
        add(f)
    push(f'_uploading master:{branch}')
    remote('rm _uploading')
