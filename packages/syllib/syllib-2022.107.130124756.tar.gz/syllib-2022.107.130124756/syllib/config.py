import os
import pickle
import sys

path = os.path.join(*sys.executable.split(os.sep), 'xes_user_configs').replace(':', ':' + os.sep)
pid = sys.argv[0].split(os.sep)[-1].split('/')[0]
try:
    pid = str(int(pid))
except:
    exit()
try:
    os.mkdir(path)
except:
    pass


class Config:
    def __init__(self, name: str = ''):
        try:
            os.mkdir(os.path.join(path, pid))
        except:
            pass
        self.path = os.path.join(path, pid, '') + name + '.pickle'
        try:
            self.attrs = pickle.load(open(self.path, 'r'))
        except FileNotFoundError:
            with open(self.path, 'w+') as f:
                pass
            self.attrs = dict()

    __getitem__ = lambda self, key: self.attrs[key]

    def __setitem__(self, key, value):
        self.attrs[key] = value

    def __delitem__(self, key):
        del self.attrs[key]

    def save(self):
        f = open(self.path, 'w+')
        f.write(pickle.dumps(self.attrs))
        f.close()

    def read(self):
        try:
            self.attrs = pickle.load(open(self.path, 'r'))
        except FileNotFoundError:
            with open(self.path, 'w+') as f:
                pass
            self.attrs = dict()
