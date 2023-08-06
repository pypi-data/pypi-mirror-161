from .api import *
from .msg import *


class NotXueersiError(RuntimeError):
    def __str__(self):
        return 'this function only use in code.xueersi.com'
