from src.utility.settings import Settings


class Logger:
    _log_file = None

    @staticmethod
    def log(x):
        if not Settings().debug_mode:
            return

        if not Logger._log_file:
            Logger._log_file = open("log.txt", "w+b", 0)

        if isinstance(x, str):
            x = x.encode('utf-8')

        Logger._log_file.write(x)