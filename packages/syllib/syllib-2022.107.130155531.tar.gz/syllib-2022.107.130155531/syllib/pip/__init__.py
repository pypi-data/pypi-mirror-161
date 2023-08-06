import os
from syllib.tools import get_run_dir

PYTHON_PATH = os.path.join(get_run_dir(), 'python.exe')


def install(package_name: str):
    os.system(f'{PYTHON_PATH} -m pip install --upgrade {package_name} -i https://pypi.org/simple')


def uninstall(package_name: str):
    os.system(f'{PYTHON_PATH} -m pip uninstall {package_name}')
