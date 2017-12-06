from src.utility.singleton import Singleton


class Versioning(metaclass=Singleton):
    MajorVersion = 0
    MinorVersion = 1
    PatchVersion = 3

    @staticmethod
    def get_version_string():
        return ".".join([str(x) for x in [Versioning.MajorVersion,
                                          Versioning.MinorVersion,
                                          Versioning.PatchVersion]])