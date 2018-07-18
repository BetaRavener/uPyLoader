import datetime
import json

from src.helpers.pyinstaller_helper import PyInstallerHelper
from src.utility.singleton import Singleton


class BuildInfo(metaclass=Singleton):
    pyinstaller_path = "build//build_info.json"

    def __init__(self):
        now = datetime.datetime.now()
        self.build_date = now.date().isoformat()

        # Try loading from pyinstaller build_info file
        self.load(PyInstallerHelper.resource_path(BuildInfo.pyinstaller_path))

    def serialize(self):
        serialized = {}
        for key, val in self.__dict__.items():
            serialized[key] = val

        return serialized

    def deserialize(self, serialized):
        deserialized = {}
        for key, val in serialized.items():
            deserialized[key] = val

        return deserialized

    def load(self, path):
        try:
            with open(path) as file:
                for key, val in self.deserialize(json.load(file)).items():
                    self.__dict__[key] = val
        except (FileNotFoundError, ValueError):
            return False

        return True

    def save(self, path):
        try:
            with open(path, "w") as file:
                json.dump(self.serialize(), file)
        except IOError:
            pass
