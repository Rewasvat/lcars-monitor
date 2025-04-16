# LCARS Monitor
Python/IMGUI App to monitor hardware sensors with a customizable LCARS-themed interface.

## Features:
* **UISystem**: a customizable graph-based GUI system integrating Widgets (UI elements), Actions (logic nodes) and Sensors (data sources).
* Different modes for the GUI:
    * **EDIT** Mode: GUI to create/see/edit/select/delete UISystems (more on this below).
    * **DISPLAY** Mode: borderless-fullscreen GUI to display a single UISystem to the user, so you can see the system you've defined while doing something else (like gaming).
* App settings, configured UISystems and other persisted data are saved to a binary file located in the user's HOME directory.

### UI System
> TODO: describe this

### Monitor EDIT Mode
> TODO: describe this


### Hardware Sensors Data
LCARSMonitor uses [LibreHardwareMonitor](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor) in order to read hardware sensor status.
This is included as a DLL in the LCARSMonitor package.


## How To Install
* As a standalone executable:
    * We build LCARS Monitor to a single executable app for ease of use: just double-clicking it will open.
    * The executable is fully packaged and should require no other dependencies to run.
    * When running it extracts its files to a temporary directory. These are deleted when the app is closed.
* As a Python Package/Tool:
    * Download this repository and `pip install .` as usual.
    * or `pip install lcarsmonitor` to download and install the package from PyPI (WIP!)
    * *This is indicated for developers working on this package or more advanced users*


## How to Use
> TODO

### Requirements to Run
* Elevated Privileges: required to be able to properly read status from all hardware in your PC. The app should by default ask the user for it through UAC.