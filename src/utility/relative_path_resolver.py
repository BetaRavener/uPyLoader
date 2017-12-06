import sys
import os
from src.utility.singleton import Singleton


class RelativePathResolver(metaclass=Singleton):
    def __init__(self):
        self._working_dir = os.path.dirname(sys.argv[0])

    def absolute(self, path):
        return os.path.join(self._working_dir, path)
