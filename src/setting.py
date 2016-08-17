from PyQt5.QtCore import QDir


class Settings:
    root_dir = QDir().currentPath()
    send_sleep = 0.1
    read_sleep = 0.1
    use_transfer_scripts = True
    wifi_presets = []

    try:
        with open("config.txt") as file:
            for line in file:
                if line.startswith("root_dir"):
                    root_dir = line.strip().split("=", 1)[1]
                elif line.startswith("send_sleep"):
                    send_sleep = float(line.strip().split("=", 1)[1])
                elif line.startswith("read_sleep"):
                    read_sleep = float(line.strip().split("=", 1)[1])
                elif line.startswith("use_transfer_scripts"):
                    use_transfer_scripts = bool(int(line.strip().split("=", 1)[1]))
                elif line.startswith("wifi_preset"):
                    value = line.strip().split("=", 1)[1]
                    name, ip, port = value.split(",")
                    wifi_presets.append((name, ip, int(port)))
    except FileNotFoundError:
        pass

    @staticmethod
    def save():
        try:
            with open("config.txt", "w") as file:
                file.write("root_dir={}\n".format(Settings.root_dir))
                file.write("send_sleep={:.3f}\n".format(Settings.send_sleep))
                file.write("read_sleep={:.3f}\n".format(Settings.read_sleep))
                file.write("use_transfer_scripts={}\n".format(int(Settings.use_transfer_scripts)))
                for preset in Settings.wifi_presets:
                    file.write("wifi_preset={},{},{}\n".format(preset[0], preset[1], preset[2]))
        except IOError:
            pass
