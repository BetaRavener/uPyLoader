# uPyLoader
## A simple tool for communicating with MicroPython board.
## The tool is in Alpha version! It may hang or crash on certain user actions. Please, restart the application in such case.
### Features:
* File upload and download over WiFi & UART
* Terminal over WiFI & UART
* Multiline input field
* Remote script execution

### Setup:
Clone this repository.
The uPyLoader runs on Python3 and requires PyQt5 and PySerial above version 3. 
Use pip to download these two via `pip install PyQt5` and `pip install pyserial>=3.1.1`.

Inside this root directory, use `python main.py` to run the application. Depending on your python setup, you may need to actually run it with `python3 main.py`. Try this if the application crashes on startup.

If having problems downloading PyQt5 on Debian distro (Ubuntu, Mint,..), try `sudo apt-get install python3-pyqt5`.
Another way to obtain PyQt5 is by [installing from source]( http://pyqt.sourceforge.net/Docs/PyQt5/installation.html#building-and-installing-from-source).

### Usage:
#### Appearance:
The main application window offers 3 colums:
* Left column shows local folder, double clicking a file opens it in the middle colum.
* Middle column shows code of selected file
* Right column shows remote (MicroPython) folder. It should be populated when connection is established, but in case not, `List Files` button can be used to do so. 
To change root directory for local folder, use `File->Navigate`.
**Note:** Local files are currently not refreshed upon external change. If you are using external editor (recommended), double-click the file in local folder to refresh it.

When connected, the application will allow opening the Terminal (`View->Terminal`).
The upper box in terminal shows output of the MicroPython on board.
Lower box is used to prepare command for the board. `Enter` key is used to send the command. `Shift-Enter` creates new line. The input also supports classic copy/paste via `Ctrl+C`, `Ctrl+V`.
The control group can be used for sending special `Ctrl-_` sequences. For example, sending `Ctrl-C` causes KeyboardInterupt and breaks any running code unless handled.

#### Connecting
On startup, the application scans for working UART connection and lists them in `Port` drop-down box. WiFi option is also listed there.
Select the desired connection port and click Connect. The status will change to green `Connected` on success.
If connecting through WiFi, make sure that you are connected to the AP of the board (otherwise the application will hang).
**Note:** If running the board for first time, set the password for WebREPL via http://micropython.org/webrepl/

#### File transfer:
File transfer for WiFi works out-of-the-box.
UART file transfer requires communication scripts on the side of board, unless this option is disabled as mentioned in Configuration section.
To upload communication scripts, use `File->Init Transfer Files`. These files greatly improve transfer speed and prevent communication errors.

To download script from MicroPython board, double click it in right, remote folder column.

To upload your script, first open it (either from local or remote folder), optionally edit it's code or set the name in lower `Filename` box and press `Save to MCU` button.

To remove script, select it by single clicking it in remote folder column and press `Remove` button.

#### File execution:
Select the file in remote folder you wish to execute (by single-clicking it) and press `Execute` button.

### Configuration:
All configuration is currently handled by `config.txt` file.
To disable using scripts in flash for file transfer over UART, set `use_transfer_scripts=0`
