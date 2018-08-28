class FileInfo:
    @staticmethod
    def is_file_binary(path: str) -> bool:
        """
        Tests if file is binary.
        :param path: Path to local file.
        :return: True if file is binary (can't be decoded with utf-8), false otherwise
        """
        with open(path, "rb") as f:
            try:
                f.read().decode("utf-8")
                return False
            except UnicodeDecodeError:
                return True
