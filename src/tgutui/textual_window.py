import logging
import traceback
from jsonrpclib import Server
from textual.app import App
from textual import on, work
from textual.timer import Timer
from textual_slider import Slider
from textual.containers import Horizontal, Vertical
from textual.widgets import Label, Button, Switch
from textual.app import ComposeResult

from tgutui.kit import Kit, TextualKit
from tgutui.rigol import Rigol
from tgutui.rpc import Rpc

class TextualWindow(App):
    """ This class contains all the Textual widgets to control the camera, scope and Pi PWM """

    DEFAULT_CSS = """
    .main {
        border: none;
        padding-left: 1;
        align: center bottom;
        content-align: center bottom;
        border-top: solid $primary-background;
        border-left: solid $primary-background;
        border-right: solid $primary-background;
    }
    Vertical > Button {
        height: 3;
        width: 100%;
        border: none;
        border-top: tall $accent;
        border-bottom: tall $accent;
        background: $primary-background;
    }
    .header {
        width: 100%;
        color: #f8ac6b;
        text-style: dim;
        border-bottom: solid $primary-background;
    }
    .border-top {
        border-top: solid $primary-background;
    }
    Vertical {
        & Label {
            width: 8;
            text-style: dim;
            color: $accent-lighten-3;
        }
        & .long_label {
           width: 12;
        }
        & .right_top {
            align: right top;
            content-align: right top;
            & Label {
                width: 9;
            }
        }
        & .data {
            height: 1;
            width: 7;
            text-style: dim;
            color: $success-lighten-1;
        }
        & .height_one {
            height: 1;
        }
        & .mag_bot_one {
            margin-bottom: 1;
        }
        & Switch {
            width: 10;
            height: 1;
            border: none;
            padding: 0 0;
            min-height: 1;
            background: $boost;
            border-left: solid $boost;
            &:focus {
                border: none;
                border-left: solid $success-lighten-1;
            }
        }
        & Slider {
            width: 25;
            height: 1;
            padding: 0 0;
            border: none;
            min-height: 1;
            background: $boost;
            &:focus {
                border: none;
                border-left: solid $success-darken-1;
            }
        }
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self.kit = TextualKit()
        self.kit.load_config()
        self.kit.adjust_font()
        if Kit.LAUNCHED:
            self.kit.resize()

        self.rigol = Rigol()
        self.rpc = Rpc(server=Kit.CAMERA_PORT, client=Kit.TEXTUAL_PORT)
        self.rpc.register(self.update_camera_data, "update_camera")
        self.rpc.register(self.textual_ack, "textual_ack")
        self.pi = Server(f"http://{Kit.PIPWM_IP}:{Kit.PIPWM_PORT}")
        self._volts_map = [0.2,0.5, 1, 2, 5]
        self._times_map = [
            0.000005,
            0.00005,
            0.0001,
            0.0002,
            0.0005,
            0.001
        ]

        self.rigol_timer: Timer = None
        self.scope_hertz = Label("", classes="data")
        self.scope_vamp = Label("", classes="data")
        self.scope_vavg = Label("", classes="data")
        self.scope_duty = Label("", classes="data")

        self.pwm_freq_slider = Slider(id="pwm_freq_slider",min=1, max=100, step=1, value=1)
        self.pwm_duty_slider = Slider(id="pwm_duty_slider",min=0, max=90, step=10, value=10)
        self.channel_slider = Slider(id="channel_slider", min=1, max=2, step=1, value=1)
        self.offset_slider = Slider(id="offset_slider", min=-2.0, max=2.0, step=0.2, value=0.0)
        self.volts_slider = Slider(id="volts_slider", min=0, max=4, step=1, value=0)
        self.time_slider = Slider(id="time_slider", min=0, max=6, step=1, value=0)
        self.pwm_freq = Label(str(self.pwm_freq_slider.value), classes="data")
        self.pwm_duty = Label(str(self.pwm_duty_slider.value), classes="data")
        self.scope_channel = Label(str(self.channel_slider.value), classes="data")
        self.scope_offset = Label(str(self.offset_slider.value), classes="data")
        self.scope_volts = Label(str(self._volts_map[self.volts_slider.value]), classes="data")
        self.scope_time = Label(str(self._times_map[self.time_slider.value] * 10000), classes="data")

        self.focus_switch = Switch(id="focus_switch")
        self.zoom_slider = Slider(id="zoom_slider",min=100, max=400, step=10, value=100,)
        self.focus_slider = Slider(id="focus_slider", min=0, max=255, step=5, value=0)
        self.pan_slider = Slider(id="pan_slider", min=-36000, max=36000, step=3600, value=0)
        self.tilt_slider = Slider(id="tilt_slider", min=-36000, max=36000, step=3600, value=0)
        self.camera_focus = Label(str(self.focus_slider.value), classes="data")
        self.camera_zoom = Label(str(self.zoom_slider.value), classes="data")
        self.camera_pan = Label(str(self.pan_slider.value), classes="data")
        self.camera_tilt = Label(str(self.tilt_slider.value), classes="data")
        self.argumented_switch = Switch(id="argumented_switch", value=False)

    def textual_ack(self):
        """ Acknowledge the connection to the camera window"""
        return True

    def update_camera_data(self, key: str, value: str | int):
        """Update the camera data based on the given property and value """
        match key:
            case "auto_focus":
                self.focus_switch.value = value
            case "focus":
                self.focus_slider.value = value
                self.camera_focus.update(str(value))
            case "zoom":
                self.zoom_slider.value = value
                self.camera_zoom.update(str(value))
            case "pan":
                self.pan_slider.value = value
                self.camera_pan.update(str(value))
            case "tilt":
                self.tilt_slider.value = value
                self.camera_tilt.update(str(value))

    def update_rigol_data(self):
        """Update the Rigol data and update the corresponding scope values.

        This method updates the Rigol data by calling the `update` method of the `rigol` object.
        It then updates the scope values (`freq`, `volt`, `vavg`, `duty`) by calling the `update` method
        of the corresponding `scope_hertz`, `scope_vamp`, `scope_vavg`, and `scope_duty` objects.

        If the `argumented_switch` value is True, it also sends the updated scope data to the RPC server
        by making requests using the `rpc` object.
        """
        self.rigol.update()
        self.scope_hertz.update(self.rigol.data.freq)
        self.scope_vamp.update(self.rigol.data.volt)
        self.scope_vavg.update(self.rigol.data.vavg)
        self.scope_duty.update(self.rigol.data.duty)
        # Much better to pass these as one dict/json
        if self.argumented_switch.value:
            self.rpc.request("set_scope_data", "date", self.rigol.data.date)
            self.rpc.request("set_scope_data", "freq", self.rigol.data.freq)
            self.rpc.request("set_scope_data", "vavg", self.rigol.data.vavg)
            self.rpc.request("set_scope_data", "duty", self.rigol.data.duty)
            self.rpc.request("set_scope_data", "volt", self.rigol.data.volt)

    @on(Switch.Changed)
    def _switch(self, event: Switch.Changed):
        """Handle the event when a switch is changed. """
        value = event.switch.value
        match event.switch.id:
            case self.focus_switch.id:
                self.focus_slider.disabled = value
                value = 1 if value else 0
                self.rpc.request("update_camera", "auto_focus", value)
            case self.argumented_switch.id:
                self.rpc.request("update_argumented", value)

    @on(Slider.Changed)
    def _slider(self, event: Slider.Changed):
        """ Handle slider events and update corresponding values. """
        value = event.slider.value
        match event.slider.id:
            case self.channel_slider.id:
                self.rigol.set_source(value)
                self.scope_channel.update(str(value))
                self._source_selected()
            case self.offset_slider.id:
                value = round(value, 2)
                self.rigol.set_offset(value)
                self.scope_offset.update(str(value))
            case self.volts_slider.id:
                value = self._volts_map[value]
                self.rigol.set_volts(value)
                self.scope_volts.update(str(value))
            case self.time_slider.id:
                value = self._times_map[value]
                self.rigol.set_time(value)
                self.scope_time.update(str(value * 10000))
            case self.pan_slider.id:
                self.rpc.request("update_camera", "pan", value)
                self.camera_pan.update(str(value))
            case self.zoom_slider.id:
                disable = True if value <= 100 else False
                self.rpc.request("update_camera", "zoom", value)
                self.camera_zoom.update(str(value))
                self.pan_slider.disabled = disable
                self.tilt_slider.disabled = disable
            case self.focus_slider.id:
                self.rpc.request("update_camera", "focus", value)
                self.camera_focus.update(str(value))
            case self.tilt_slider.id:
                self.rpc.request("update_camera", "tilt", value)
                self.camera_tilt.update(str(value))
            case self.pwm_duty_slider.id:
                if Kit.USE_PIPWM:
                    self.pi.change_duty(value)
                    self.pwm_duty.update(str(value))
            case self.pwm_freq_slider.id:
                if Kit.USE_PIPWM:
                    self.pi.change_frequency(value)
                    self.pwm_freq.update(str(value))


    @on(Button.Pressed)
    def _button(self, event: Button.Pressed):
        """ Handle button events. """
        match event.button.id:
            case "quit_btn":
                self.rpc.request("close_window")
                self.stop()

    def _source_selected(self):
        """
        Updates the offset, volts, and time sliders based on the current settings of the Rigol device.
        """
        if not Kit.USE_RIGOL:
            return
        self.offset_slider.value = self.rigol.get_offset()
        volts = self._volts_map.index(self.rigol.get_volts())
        times = self._times_map.index(self.rigol.get_time())
        self.volts_slider.value = volts
        self.time_slider.value = times

    def on_mount(self):
        """
        This method is called when the component is mounted.
        It checks if the RPC is started, sets up a timer to update Rigol data,
        and initializes the channel slider value.
        """
        self.rpc.check_started()
        self.rigol_timer = self.set_interval(0.25, self.update_rigol_data)
        self.channel_slider.value = self.rigol.get_source()
        
    @work(exclusive=True, thread=True)
    def start_worker(self):
        """
        Starts the worker by connecting to the Rigol and RPC devices.
        If an exception occurs during the connection process, it is logged and the worker is stopped.
        """
        try:
            self.rigol.connect()
            self.rpc.connect()
        except Exception:
            logging.error(f"{traceback.format_exc()}")
            self.stop()

    def stop(self):
        """ Stop the textual window services """
        if self.rigol_timer:
            self.rigol_timer.stop()
        self.rpc.disconnect()
        self.rigol.disconnect()
        App.exit(self)

    def compose(self) -> ComposeResult:
        """ Compose the window """
        self.start_worker()
        with Vertical(classes="main"):
            yield Label("PWM", classes="header")
            with Horizontal():
                yield Label("Duty")
                yield self.pwm_duty
                yield self.pwm_duty_slider
            with Horizontal():
                yield Label("KHz")
                yield self.pwm_freq
                yield self.pwm_freq_slider
            yield Label("Oscilloscope", classes="header border-top")
            with Horizontal(classes="right_top height_one"):
                yield Label("KHz")
                yield Label("Duty")
                yield Label("Volts")
                yield Label("VAvg")
            with Horizontal(classes="right_top height_one mag_bot_one"):
                yield self.scope_hertz
                yield self.scope_duty
                yield self.scope_vamp
                yield self.scope_vavg
            with Horizontal():
                yield Label("Channel")
                yield self.scope_channel
                yield self.channel_slider
            with Horizontal():
                yield Label("Offset")
                yield self.scope_offset
                yield self.offset_slider
            with Horizontal():
                yield Label("Volts")
                yield self.scope_volts
                yield self.volts_slider
            with Horizontal():
                yield Label("Time us")
                yield self.scope_time
                yield self.time_slider
            yield Label("Camera", classes="header border-top")
            with Horizontal():
                yield Label("Argumented", classes="long_label")
                yield self.argumented_switch
            with Horizontal():
                yield Label("Auto Focus", classes="long_label")
                yield self.focus_switch
            with Horizontal():
                yield Label("Focus")
                yield self.camera_focus
                yield self.focus_slider
            with Horizontal():
                yield Label("Zoom")
                yield self.camera_zoom
                yield self.zoom_slider
            with Horizontal():
                yield Label("Pan")
                yield self.camera_pan
                yield self.pan_slider
            with Horizontal():
                yield Label("Tilt")
                yield self.camera_tilt
                yield self.tilt_slider
            yield Button("Close", id="quit_btn")


if __name__ == "__main__":
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
