# uPyLoader
## A simple tool for communicating with MicroPython board.
## The tool is in Alpha version! It may hang or crash on certain user actions. Please, restart the application in such case.
### Features:
* File upload and download over WiFi & UART
* Terminal over WiFI & UART
* Multiline input field with history
* Remote script execution
* Graphical interface for flashing firmware (via esptool)
* Editing via built-in or external editor

### Setup:
Clone this repository.
The uPyLoader runs on Python3 and requires PyQt5 and PySerial above version 3. 
Use pip to download these two via `pip install PyQt5` and `pip install pyserial>=3.1.1`. OS-X users can also use script ` 	install_osx_dependencies.sh` in root directory provided by @sarusso to install dependencies automatically. 

Inside this root directory, use `python main.py` to run the application. Depending on your python setup, you may need to actually run it with `python3 main.py`. Try this if the application crashes on startup.

If having problems downloading PyQt5 on Debian distro (Ubuntu, Mint,..), try `sudo apt-get install python3-pyqt5`.
Another way to obtain PyQt5 is by [installing from source]( http://pyqt.sourceforge.net/Docs/PyQt5/installation.html#building-and-installing-from-source).

### Usage:
#### Appearance:
The main application window offers 2 colums:
* Left column shows local folder, double clicking a file opens it in Code Editor.
* Right column shows remote (MicroPython) folder. It should be populated when connection is established, but in case not, `List Files` button can be used to do so. Again, double clicking file opens it in Code Editor.
To change root directory for local folder, use `File->Navigate`.

When connected, the application will allow opening the Terminal (`View->Terminal`).
The upper box in terminal shows output of the MicroPython on board.
Lower box is used to prepare command for the board. `Enter` key is used to send the command. `Shift-Enter` creates new line. The input also supports classic copy/paste via `Ctrl+C`, `Ctrl+V`. To browse through previous commands (input history), use `Ctrl+UpArrow` and `Ctrl+DownArrow`.
The control group can be used for sending special `Ctrl-_` sequences. For example, sending `Ctrl-C` causes KeyboardInterupt and breaks any running code unless handled.

Code editor has single main element that shows script code. The editor is populated by double-clicking `.py` scripts in either of the main window's columns. The code can be either saved to local file or uploaded to remote device by using the `Save` buttons above the code editor element.
**Note:** Local files are currently not refreshed upon external change. If you are using external editor (recommended), double-click the file in local folder to refresh it.

#### Connecting
On startup, the application scans for working UART connection and lists them in `Port` drop-down box. WiFi option is also listed there.
Select the desired connection port and click Connect. The status will change to green `Connected` on success.
If connecting through WiFi, make sure that you are connected to the AP of the board (otherwise the application will hang).
**Note:** If running the board for first time, set the password for WebREPL via http://micropython.org/webrepl/

#### File transfer:
File transfer for WiFi works out-of-the-box.
UART file transfer requires communication scripts on the side of board, unless this option is disabled as mentioned in Configuration section.
To upload communication scripts, use `File->Init Transfer Files`. These files greatly improve transfer speed and prevent communication errors.

To download file from MicroPython board, select it in the right, remote folder column and press `Transfer` underneath. The script will be transfered to a folder specified in `PC path` with the same name it had on the remote device. 

To upload file, select it in left, local folder column, optionally edit it's name underneath in the `MCU name` box and press `Transfer` next to it.

To remove script, select it by single clicking it in remote folder column and press `Remove` button.

#### File execution:
Select the file in remote folder you wish to execute (by single-clicking it) and press `Execute` button.

#### Flashing firmware (only for ESP8266):
Open dialog by selecting `File->Flash firmware`. Because of mismatch between python version (uPyLoader == Python3, esptool == Python2), it is required that you select Python2 executable of environment which contains esptool (esptool can be added to environment with `pip install esptool`). In case that this executable can be called directly (e.g. on linux), it is sufficient to type `python` into `Python2 path` field. Otherwise, full path to executable must be specified. You can use `Pick` button next to the input field for browsing through directories. An example of full path on Windows is `C:/Python27/python.exe`.

Once correct Python2 executable is selected, choose firmware file that you would like to flash to ESP8266. Either enter full path to `Firmware file` field or use `Pick` button to browse. You can also choose if you would like to erase flash prior to writing new firmware by checking `Erase flash` (this operation takes aprox. 10 seconds). Select communication port from `Port` drop-down and check if you have ESP8266 wired up correctly (the correct wiring can be seen by clicking on `Wiring instructions`). If everything is in order, press Flash button. The `Flasher output` text-box should show progress of the operation and end with message `Rebooting from flash mode...` if successful. 

### Configuration:
All configuration is currently handled by `config.txt` file.
To disable using scripts in flash for file transfer over UART, set `use_transfer_scripts=0`

## Changelog:
### 2016-08-17:
* The main GUI is now two-pane layout supporting file transfer between local host (PC) and remote device (MCU)
* Code editor became separate window which can be used to edit scripts in-place. Previous file-save functionality is preserved for fast workflow.
* UART communication protocol was changed to support transfer of binary files. The transfer scripts in the MCU needs to be updated. Use `File->Init Transfer Files` to do so.
