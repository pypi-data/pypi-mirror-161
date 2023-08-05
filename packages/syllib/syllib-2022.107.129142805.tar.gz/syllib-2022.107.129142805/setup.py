from setuptools import setup, find_packages

from syllib.__init__ import __version__

NAME = 'syllib'
VERSION = __version__
AUTHOR = 'suyiyi'
AUTHOR_EMAIL = '3274719101@qq.com'
URL = 'https://github.com/a-suyiyi/mylib'

setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    install_requires=[
        'requests'
    ],
    packages=find_packages()
)
