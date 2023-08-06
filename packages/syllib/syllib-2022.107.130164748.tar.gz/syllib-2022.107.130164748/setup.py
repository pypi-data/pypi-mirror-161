from setuptools import setup, find_packages

from syllib.__init__ import __version__

NAME = 'syllib'
VERSION = __version__
AUTHOR = 'suyiyi'
AUTHOR_EMAIL = '3274719101@qq.com'
URL = 'https://github.com/a-suyiyi/syllib'
DESCRIPTION = 'suyiyi\'s package'
try:
    with open('README.md', 'r') as f:
        LONG_DESCRIPTION = f.read()
except:
    LONG_DESCRIPTION = ''

# print(LONG_DESCRIPTION)

setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    install_requires=[
        'requests'
    ],
    packages=find_packages()
)
