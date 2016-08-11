from PyQt5.QtCore import QDir


class Settings:
    root_dir = QDir().currentPath()
    send_sleep = 0.1
    read_sleep = 0.1
    use_transfer_scripts = True

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

    @staticmethod
    def save():
        with open("config.txt", "w") as file:
            file.write("root_dir={}\n".format(Settings.root_dir))
            file.write("send_sleep={:.3f}\n".format(Settings.send_sleep))
            file.write("read_sleep={:.3f}\n".format(Settings.read_sleep))
            file.write("use_transfer_scripts={}\n".format(int(Settings.use_transfer_scripts)))
