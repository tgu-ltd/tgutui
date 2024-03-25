""" This file starts either the3 Textual or Camera window """

import sys
import logging
from tgutui.kit import Kit
from tgutui.camera_window import CameraWindow
from tgutui.textual_window import TextualWindow


if __name__ == "__main__":
    if "camera_window" in sys.argv:
        Kit.create_log(file="camera_window.log")
        with CameraWindow() as window:
            window.display()

    if "textual_window" in sys.argv:
        Kit.create_log(file="textual_window.log")
        window = TextualWindow()
        try:
            window.run()
        except (KeyboardInterrupt, Exception) as e:
            logging.error(f"{e}")
            window.stop()
            window.exit()
        if not Kit.DEBUG:
            Kit.close_window()
