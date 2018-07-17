import json
import os

from PyQt5.QtCore import QByteArray
from PyQt5.QtCore import QDir
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence

from src.utility.relative_path_resolver import RelativePathResolver
from src.utility.singleton import Singleton


class Settings(metaclass=Singleton):
    newest_version = 101

    def __init__(self):
        self.version = 100  # Assume oldest config
        self.root_dir = QDir().currentPath()
        self.send_sleep = 0.1
        self.read_sleep = 0.1
        self.use_transfer_scripts = True
        self.use_custom_transfer_scripts = False
        self.external_transfer_scripts_folder = None
        self.wifi_presets = []
        self.python_flash_executable = None
        self.last_firmware_directory = None
        self.debug_mode = False
        self._geometries = {}
        self.external_editor_path = None
        self.external_editor_args = None
        self.new_line_key = QKeySequence(Qt.SHIFT + Qt.Key_Return, Qt.SHIFT + Qt.Key_Enter)
        self.send_key = QKeySequence(Qt.Key_Return, Qt.Key_Enter)
        self.terminal_tab_spaces = 4
        self.mpy_cross_path = None
        self.preferred_port = None
        self.auto_transfer = False

        if not self.load():
            if not self.load_old():
                # No config found, init at newest version
                self.version = Settings.newest_version
                return

        self._update_config()

    def serialize(self):
        serialized = {}
        for key, val in self.__dict__.items():
            if isinstance(val, QKeySequence):
                val = val.toString()

            serialized[key] = val

        return serialized

    def deserialize(self, serialized):
        deserialized = {}
        for key, val in serialized.items():
            if key == "new_line_key" or key == "send_key":
                val = QKeySequence(val)

            deserialized[key] = val

        return deserialized

    def load(self):
        try:
            with open(RelativePathResolver().absolute("config.json")) as file:
                for key, val in self.deserialize(json.load(file)).items():
                    self.__dict__[key] = val
        except (FileNotFoundError, ValueError):
            return False

        return True

    def _update_config(self):
        if self.version < 101:
            # Presets now have password, add it if missing
            for preset in self.wifi_presets:
                if len(preset) == 3:
                    preset.append(None)

        self.version = Settings.newest_version

    def load_old(self):
        try:
            with open(RelativePathResolver().absolute("config.txt")) as file:
                for line in file:
                    if line.startswith("root_dir"):
                        self.root_dir = line.strip().split("=", 1)[1]
                    elif line.startswith("send_sleep"):
                        self.send_sleep = float(line.strip().split("=", 1)[1])
                    elif line.startswith("read_sleep"):
                        self.read_sleep = float(line.strip().split("=", 1)[1])
                    elif line.startswith("use_transfer_scripts"):
                        self.use_transfer_scripts = bool(int(line.strip().split("=", 1)[1]))
                    elif line.startswith("wifi_preset"):
                        value = line.strip().split("=", 1)[1]
                        name, ip, port = value.split(",")
                        self.wifi_presets.append((name, ip, int(port)))
                    elif line.startswith("python_flash_executable"):
                        self.python_flash_executable = line.strip().split("=", 1)[1]
                    elif line.startswith("last_firmware_directory"):
                        self.last_firmware_directory = line.strip().split("=", 1)[1]
        except FileNotFoundError:
            return False

        return True

    def save(self):
        config_file = RelativePathResolver().absolute("config.json")
        try:
            # Check if file exists (supports also hidden files)
            if os.path.isfile(config_file):
                # Use write mode that also works with hidden files
                with open(os.open(config_file, os.O_WRONLY | os.O_TRUNC), 'w') as file:
                    json.dump(self.serialize(), file)
            else:
                # Simply create a new file
                with open(config_file, "w") as file:
                    json.dump(self.serialize(), file)
        except IOError:
            pass

    def update_geometry(self, name, geometry):
        self._geometries[name] = list(geometry.data())

    def retrieve_geometry(self, name):
        if name not in self._geometries:
            return None

        return QByteArray(bytes(self._geometries[name]))
