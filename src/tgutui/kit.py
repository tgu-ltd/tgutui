
import os
import sys
from typing import Callable
import shlex
import logging
import subprocess
import shutil
import tgutui

class Kit:
    """ This class is a wrapper around the kitten command line tool """

    _LOGGER = logging.getLogger()
    _HAVE_KITTEN: bool = shutil.which("kitten") is not None
    PIPWM_IP: str = os.environ.get("PIPWM_IP", "127.0.0.1")
    PIPWM_PORT: int = int(os.environ.get("PIPWM_PORT", 34962))
    RIGOL_IP: str = os.environ.get("RIGOL_IP", "127.0.0.1")
    CAMERA_DEVICE: int = int(os.environ.get("CAMERA_DEVICE", 0))
    CAMERA_PORT: int = int(os.environ.get("CAMERA_PORT", 33761))
    TEXTUAL_PORT: int = int(os.environ.get("TEXTUAL_PORT", 33962))
    CAMERA_TITLE: str = os.environ.get("CAMERA_TITLE", "CAMERA_TITLE")
    TEXTUAL_TITLE: str = os.environ.get("TEXTUAL_TITLE", "TEXTUAL_TITLE")
    CAMERA_CMD: str = os.environ.get("CAMERA_CMD", "python -m tgutui camera_window")
    TEXTUAL_CMD: str = os.environ.get("TEXTUAL_CMD", "python -m tgutui textual_window")
    DEBUG: bool = True if os.environ.get("DEBUG", "1") == "1" else False
    LOG_RPC: bool = True if os.environ.get("LOG_RPC", "1") == "1" else False
    LAUNCHED: bool = False if os.environ.get("LAUNCHED", "0") == "0" else True
    USE_PIPWM: bool = False if os.environ.get("USE_PIPWM", "0") == "0" else True
    USE_RIGOL: bool = False if os.environ.get("USE_RIGOL", "0") == "0" else True
    SHOW_CAMERA: bool = False if os.environ.get("SHOW_CAMERA", "0") == "0" else True
    CONFIG_FILE: str = f"{tgutui.__path__[0]}/{os.environ.get('CONFIG_FILE', 'window.conf')}"

    def __init__(self) -> None:
        logging.info(f"Kit: {repr(self)}")

    def kitten(fn: Callable):
        def decorate(*args, **kwargs):
            if not Kit._HAVE_KITTEN:
                logging.error("Kitten not found")   
                return None
            fn(*args, **kwargs)
        return decorate

    def __repr__(self) -> str:
        r = f"\n DEBUG: {Kit.DEBUG}\n"
        r = f"{r} RIGOL: {Kit.RIGOL_IP}\n"
        r = f"{r} LOG_RPC: {Kit.LOG_RPC}\n"
        r = f"{r} LAUNCHED: {Kit.LAUNCHED}\n"
        r = f"{r} USE_RIGOL: {Kit.USE_RIGOL}\n"
        r = f"{r} USE_PIPWM: {Kit.USE_PIPWM}\n"
        r = f"{r} CAMERA: {Kit.CAMERA_DEVICE}\n"
        r = f"{r} KITTEN: {Kit._HAVE_KITTEN}\n"
        r = f"{r} SHOW_CAMERA: {Kit.SHOW_CAMERA}\n"
        r = f"{r} CAMERA_PORT: {Kit.CAMERA_PORT}\n"
        r = f"{r} TEXTUAL_PORT: {Kit.TEXTUAL_PORT}\n"
        r = f"{r} PIPWM_IP: {Kit.PIPWM_IP}\n"
        r = f"{r} PIPWM_PORT: {Kit.PIPWM_PORT}\n"
        return r

    @kitten
    @staticmethod
    def cmd(cmd: str):
        """ Run a command using kitten"""
        try:
            # Could check to see if --no-response is in the command
            # and test the return code to make sure it completed
            subprocess.check_output(
                ["kitten", "@"] + shlex.split(cmd),
                stderr=subprocess.STDOUT,
                timeout=0.3,
            )
        except subprocess.TimeoutExpired:
            pass

    @kitten
    @staticmethod
    def close_window():
        """ Close the current window"""
        Kit.cmd("close-window --self --no-response")

    @staticmethod
    def create_log(file: str, level: int = logging.INFO):
        """ Create a log file """
        if not Kit.DEBUG:
            return
        logging.basicConfig(
            level=level,
            filemode="w",
            filename=file,
            format='%(levelname)s[%(pathname)s:%(funcName)s:%(lineno)d] - %(message)s'
        )


if not Kit.LAUNCHED:
    for index, arg in enumerate(sys.argv):
        __ARGV = None
        try:
            __ARGV = sys.argv[index + 1]
        except IndexError:
            continue
        attr = getattr(Kit, arg, None)
        if attr is None:
            continue
        if isinstance(attr, bool):
            if __ARGV in ["1", "true", "True", "TRUE"]:
                setattr(Kit, arg, True)
            else:
                setattr(Kit, arg, False)
        elif isinstance(attr, int):
            try:
                __ARGV = int(__ARGV)
                setattr(Kit, arg, __ARGV)
            except ValueError:
                setattr(Kit, arg, __ARGV)
        else:
            setattr(Kit, arg, __ARGV)

class CameraKit(Kit):
    """ This class is a wrapper around the camera window"""

    def resize(self, width: int, height: int):
        """ Resize the window"""
        cmd = "resize-os-window --action resize --unit pixels"
        cmd = f"{cmd} --width {width} --height {height} --self --no-response"
        Kit.cmd(cmd)

    def set_background(self, img_path: str):
        """ Set the background image for the window"""
        Kit.cmd(f"set-background-image {img_path}")


    def launch_textual_window(self):
        """ Launch the textual window"""
        hold  = "--hold" if Kit.DEBUG else ""
        Kit.cmd(f"launch \
                --title {Kit.TEXTUAL_TITLE} \
                --cwd current \
                --copy-env \
                --location after \
                --no-response \
                {hold} {Kit.TEXTUAL_CMD} \
        ")

class TextualKit(Kit):
    """ This class is a wrapper around the textual window"""

    def load_config(self):
        """ Load the configuration file"""
        Kit.cmd(f"load-config --no-response {Kit.CONFIG_FILE}")

    def resize(self):
        """ Resize the window"""
        Kit.cmd("resize-window --self -i -18")

    @staticmethod
    def adjust_font():
        """ Adjust the font size"""
        Kit.cmd("set-font-size -- -4")
