# LCARS Monitor
Windows WPF App to monitor hardware status with a customizable LCARS-themed interface.

## Features:
* Stays in System Tray
* The following windows which can be opened from the app in tray:
    * **Monitor:** custom interface to monitor hardware (more on this below)
    * **Editor:** allows the customization of the Monitor window.
* Saves settings to a local JSON

### Monitor Window
The Monitor shows the user-defined interface to monitor his hardware.

This is based on a set of control widgets with simplified configuration and with Star Trek LCARS themes.
With simple configuration the user can place panels, buttons, images, bars, labels and more in order to build a LCARS interface to:
* Show Hardware Status
    * Supports multiple CPU/GPU/Motherboard/RAM/Storage Devices/Network hardware
    * Support several sensors: power, load, frequency, temperature, and more.
* Show alerts when some sensor reaches critical values
    * And alerts can be customized as well
* Supports different "tabs" of widgets:
    * User can configure multiple tabs.
    * The monitor shows a single tab of widgets.
    * A tab can have a control that when pressed, switches "selected tab" to another one.
* Support simple external commands:
    * allows some controls to open an external program or run a script.


## Requirements to Run
* Elevated Privileges: required to be able to properly read status from all hardware in your PC. The app should by default ask the user for it through UAC.
* x64 system
* .NET framework
    > TODO: which?

### Dependencies
List of dependencies used by LCARS Monitor.
* .NET / WPF
* [LibreHardwareMonitor](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor): in order to read hardware sensor status.
* [XAML Export](https://www.mikeswanson.com/xamlexport/): Adobe Illustrator plugin to export vector assets directly as XAML to use with WPF.


## How To Install
The build should be a standalone application, without need to "install" per-se.
Just extract the application to a folder of your choosing, and run the executable.

## How to Use
> TODO