import PyQt5.uic
import os
import re


def map(dirName, fileName):
    return './gui', fileName


def next_line_start(content, idx):
    end = False
    while True:
        if idx >= len(content):
            return -1
        if end:
            if content[idx] != "\n" and content != "\r":
                return idx
        else:
            if content[idx] == "\n" or content == "\r":
                end = True
                continue
        idx += 1


def change_controls_path(content):
    content = content.replace("from transfertreeview import TransferTreeView",
                              "from src.gui.controls.transfer_tree_view import TransferTreeView")
    return content


def replace_resources(file_path):
    with open(file_path, "r") as f:
        content = f.read()
        content = change_controls_path(content)
        # Reference PyInstallerHelper in each file (at correct place -- after other imports)
        last_import_idx = content.rfind("import")
        next_line_idx = next_line_start(content, last_import_idx)
        content = "".join([content[:next_line_idx],
                           "\n# Added by buildgui.py script to support pyinstaller\n",
                           "from src.helpers.pyinstaller_helper import PyInstallerHelper\n\n",
                           content[next_line_idx:]])

        # Envelope all icon resources with path resolution
        p = re.compile(r"(\"icons/[^\"]*\")")
        content = p.sub(r"PyInstallerHelper.resource_path(\1)", content)
    with open(file_path, "w") as f:
        f.write(content)


def main():
    PyQt5.uic.compileUiDir('./gui/qt', map=map)

    for file in os.listdir('./gui'):
        file_path = "./gui/" + file
        if (not os.path.isfile(file_path)) or file.startswith("__"):
            continue
        replace_resources(file_path)


main()
