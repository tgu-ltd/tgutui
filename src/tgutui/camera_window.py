import os
import sys
import time
import logging
import traceback
from threading import Thread
from subprocess import CalledProcessError
from rich.table import Table
from rich.console import Console

from tgutui.rpc import Rpc
from tgutui.camera import Camera
from tgutui.kit import Kit, CameraKit
from tgutui.rigol import ScopeData

class CameraWindow:
    """ The camera window class that will display the camera argumented data"""

    CTRL_WIDTH = 400

    def __init__(self):
        super().__init__()
        self._errors = 0
        self.camera = Camera()
        self.kit = CameraKit()
        self._argumented = False
        self.scope = ScopeData()
        self.console = Console(stderr=False)
        self.rpc = Rpc(server=Kit.TEXTUAL_PORT, client=Kit.CAMERA_PORT)
        self.rpc.register(self.remote_close, "close_window")
        self.rpc.register(self.update_camera, "update_camera")
        self.rpc.register(self.set_scope_data, "set_scope_data")
        self.rpc.register(self.update_argumented, "update_argumented")
        self._rpc_thread = Thread(target=self.rpc.connect, daemon=True)
        self._quit_thread = Thread(target=self._quit_delay)
        width = int(self.camera.data.width + CameraWindow.CTRL_WIDTH)
        self.kit.resize(height=int(self.camera.data.height), width=width)
        if not Kit.LAUNCHED or not Kit.SHOW_CAMERA:
            self.update_argumented(True)

    def update_argumented(self, state: bool):
        """ Update the argumented state of the window"""
        self._argumented = state
        if not state:
            os.system("clear")

    def set_scope_data(self, property: str, value: str):
        """ Set the scope data. This is called by the Textual Window"""
        # Much better to pass these as one dict/json
        match property:
            case "date":
                self.scope.date = value
            case "freq":
                self.scope.freq = value
            case "vavg":
                self.scope.vavg = value
            case "duty":
                self.scope.duty = value
            case "volt":
                self.scope.volt = value

    def update_camera(self, property: str, value: str | int):
        """ Update the camera data. This is called by the Textual Window"""
        # Much better to pass these as one dict/json
        match property:
            case "auto_focus":
                self.camera.set_auto_focus(value)
            case "focus":
                self.camera.set_focus(value)
            case "pan":
                self.camera.set_pan(value)
            case "tilt":
                self.camera.set_tilt(value)
            case "zoom":
                self.camera.set_zoom(value)

    def remote_close(self):
        """ Close the window remotely. This is called by the Textual Window"""
        self._quit_thread.start()

    def _quit_delay(self):
        time.sleep(1)
        self.close()


    def show_argumented(self):
        """ Update the rich console with the scope and camera data"""
        if not self._argumented:
            return
        self.console.clear()
        self.console.print("\n")
        t = Table(show_header=False, expand=True, box=None)
        t.add_column(" Scope", style="black", justify="right")
        t.add_column("", style="blue", justify="left")
        t.add_column(" Camera", style="black", justify="right")
        t.add_column("", style="blue", justify="left")
        t.add_row("Freq", str(self.scope.freq), "Auto", str(self.camera.data.auto_focus))
        t.add_row("Duty", str(self.scope.duty), "Zoom", str(self.camera.data.zoom))
        t.add_row("VAmp", str(self.scope.volt), "Focus", str(self.camera.data.focus))
        t.add_row("VAvg", str(self.scope.vavg), "Tilt", str(self.camera.data.tilt))
        t.add_row("", "", "Pan", str(self.camera.data.pan))
        self.console.print(t)

    def start_textual_window(self):
        """ Start the textual window and wait for it to acknowledge the connection"""
        textual_ack = False
        if Kit.LAUNCHED:
            self.kit.launch_textual_window()
        time.sleep(1)
        for _ in range(10):
            time.sleep(0.2)
            try:
                self.rpc.request("textual_ack")
                textual_ack = True
            except ConnectionRefusedError:
                continue

        if not textual_ack and not Kit.DEBUG:
            logging.error("Textual Window did not start")
            self.close()
            return

        # Update the window
        for key in self.camera.data.__dict__.keys():
            value = getattr(self.camera.data, key)
            self.rpc.request("update_camera", key, value)

    def open(self):
        """ Open the window and start the rpc server"""
        self.camera.open()
        self._rpc_thread.start()
        self.rpc.check_started()
        self.start_textual_window()


    def close(self):
        """ Close the window and stop the rpc server"""
        self.camera.close()
        self.rpc.disconnect()
        try:
            self._quit_thread.join()
        except RuntimeError as e:
            logging.error(f"CW: {e}")
        try:
            self._rpc_thread.join()
        except RuntimeError as e:
            logging.error(f"CW: {e}")

        if not Kit.DEBUG:
            Kit.close_window()

    def display(self):
        """ Display the camera window and update the rich console"""
        last_update = time.time()
        while self.rpc.running:
            try:
                if time.time() > last_update + 0.33:
                    last_update = time.time()
                    self.show_argumented()
                if Kit.SHOW_CAMERA:
                    self.camera.save()
                    self.kit.set_background(img_path=Camera.OUTPUT)
                    self._errors  = 0       
                else:
                    time.sleep(0.1)
            except CalledProcessError:
                self._errors += 1
                if self._errors > 10:
                    logging.error("To many errors")
                    self.close()
                    break
                continue
            except Exception as e:
                logging.error(f"{traceback.format_exc()}")
                self.close()
                raise e

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *_):
        self.close()


if __name__ == "__main__":
    Kit.create_log(file="camera_window.log")
    with CameraWindow() as window:
        window.display()
