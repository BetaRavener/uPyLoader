import PyQt5.uic


def map(dirName, fileName):
    return './gui', fileName


PyQt5.uic.compileUiDir('./gui/qt', map=map)
