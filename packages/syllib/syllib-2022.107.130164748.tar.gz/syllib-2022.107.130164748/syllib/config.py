import os
import pickle

from .tools.api import get_run_dir, safe_create_dir
from .xes import get_pid

path = os.path.join(get_run_dir(), 'xes_user_configs')
pid = str(get_pid())

safe_create_dir(os.path.join(path, pid))


class Config:
    attrs: dict
    path: str
    auto_save: bool

    def __init__(self, name: str = '', auto_save: bool = True):
        self.attrs = dict()
        self.path = os.path.join(path, pid, f'#{name}.pickle')
        self.auto_save = auto_save
        self.read()

    def __getitem__(self, key):
        return self.attrs.__getitem__(key)

    def __setitem__(self, key, value):
        if self.auto_save:
            self.read()
        self.attrs.__setitem__(key, value)
        if self.auto_save:
            self.save()

    def __delitem__(self, key):
        if self.auto_save:
            self.read()
        self.attrs.__delitem__(key)
        if self.auto_save:
            self.save()

    def save(self):
        f = open(self.path, 'wb+')
        f.write(pickle.dumps(self.attrs))
        f.close()

    def read(self):
        try:
            self.attrs = pickle.load(open(self.path, 'rb'))
        except FileNotFoundError:
            self.save()


