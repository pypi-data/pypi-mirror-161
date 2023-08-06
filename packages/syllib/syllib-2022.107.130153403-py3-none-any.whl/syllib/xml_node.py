class Node: pass


class Node:
    def __init__(self, name: str, content='', **attrs):
        self.name = name
        self.children = list()
        self.attrs = attrs
        self.content = content

    def appendchild(self, c: Node):
        self.children.append(c)

    def __repr__(self):
        s = ''
        for k in self.attrs.keys(): s += ' %s="%s"' % (k, self.attrs[k])
        return '<%s%s>\n' % (self.name, s) + '\n'.join(map(repr, self.children)) + '\n</%s>' % self.name

    __str__ = lambda self: self.__repr__()

    def write(self, file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None):
        f = open(file=file, mode=mode, buffering=buffering, encoding=encoding, errors=errors, newline=newline,
                 closefd=closefd, opener=opener)
        f.write(self.__repr__())
        f.close()

    def __getitem__(self, s):
        return self.attrs[s]

    def __setitem__(self, s, v):
        self.attrs[s] = v

    def __delitem__(self, s):
        del self.attr[s]
