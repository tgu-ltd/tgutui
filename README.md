# The TGUTUI

## A Terminal Operating Test Equipment

**Warning**: They'll be dragons

**Note**: This is an experimental project for demonstration purposes only

**See**: This [Youtube](https://www.youtube.com/watch?v=uiTUZpZKRJw) demonstration to see it working

**Image** ![ScreenShot](https://www.tgu-ltd.uk/img/tgutui.png)

## Overview

This python application utilizes some of the latest linux terminal tools to interface with test equipment.
Its primary purpose is demonstrate what can be done in a terminal with the Kitty terminal and T.

It includes the following features:

* A [Kitty Terminal](https://sw.kovidgoyal.net/kitty/quickstart/):
  * That allows background images to be displayed
  * That allows [Rich](https://pypi.org/project/rich/) text to be overlaid

* A [Textual](https://textual.textualize.io/) Application:
  * That can control a USB Web Cam via opencv-python
  * That can control a Oscilloscope via PyVisa
  * That can control a Raspberry Pi Zero Hardware PWM via Rpc

## Software Used

* [Kitty Terminal](https://sw.kovidgoyal.net/kitty/quickstart/)
* Python Packages
  * [Textual](https://textual.textualize.io/)
  * [Textual-slider](https://pypi.org/project/textual-slider/)
  * [PyVisa](https://pypi.org/project/PyVISA/)
  * [PyVISA-py](https://pypi.org/project/PyVISA-py/)
  * [opencv-python](https://pypi.org/project/opencv-python/)
  * [jsonrpclib-pelix](https://pypi.org/project/jsonrpclib-pelix/)

## How It Works

The following sudo steps give an overview off how the application works

1. From within a poetry environment run the launch.sh script
2. The script then opens Kitty os terminal window
3. The Kitty terminal runs the camera_window.py code
4. The camera_window.py code
   1. Loads the camera modules
   2. Registers RPC methods
   3. Starts another Kitty terminal
   4. Waits for new kitty terminal to load
5. The new Kitty terminal then runs the textual_window.py code
6. The textual_window.py code starts a Textual application
7. The Textual application
      1. Connects to the Oscilloscope and polls for data
      2. Registers RPC methods
8. The camera_window.py code then sends camera data to the textual_window.py code
9. The application has started

## Installation

For this project to work the following is required ...

### Hardware

* PC / Laptop
* Logitech StreamCam
* Rigol 1054Z Oscilloscope
* Rapberry Pi Zero W with 32bit Raspbian lite installed
* A Signal Generator, not essential but good to have

### Software

* A linux OS with the following packages installed:
  * [Kitty Terminal](https://sw.kovidgoyal.net/kitty/quickstart/)
  * [poetry](https://python-poetry.org/)
  * Python version >= 3.11

## To Install and Run

```bash
$ git clone this repo
$ cd tgutui
$ chmod +x launch.sh
$ poetry install
$ poetry shell
$ ./launch.sh
```


## Configuration

The `launch.sh` script contains all the configuration options the application uses
