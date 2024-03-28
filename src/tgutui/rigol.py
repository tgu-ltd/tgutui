import logging
import datetime
from dataclasses import dataclass
from typing import Callable

import pyvisa
from tgutui.kit import Kit


@dataclass
class ScopeData:
    """ A class for scope data to be hauled around """
    date: str = ""
    freq: str = ""
    volt: str = ""
    duty: str = ""
    vavg: str = ""
    def __repr__(self) -> str:
        return "{self.date}, {self.freq}, {self.volt}, {self.duty}, {self.vavg}"

class Rigol:
    """ Rigol class to communicate with a 1054Z via SCPI """
    def __init__(self) -> None:
        self._ip: str | None = Kit.RIGOL_IP if Kit.RIGOL_IP != "127.0.0.1" else None
        self._instrument: pyvisa.ResourceManager = None
        self._connected: bool = False
        self._data = ScopeData()
        self._channel = 1

    def connect(self) -> None:
        """ Connect to the scope """
        if not Kit.USE_RIGOL:
            return
        if not self._ip:
            logging.error("Rigol: No IP address provided.")
            return None
        self._instrument = pyvisa.ResourceManager().open_resource(
            resource_name=f"TCPIP::{self._ip}::inst0::INSTR",
            write_termination='\n',
            read_termination='\n',
        )
        if not self._instrument.query("*IDN?"):
            self.disconnect()
            raise RuntimeError("No IDN")
        self._connected = True

    @property
    def data(self) -> ScopeData:
        """ The the scope data """
        return self._data

    def connected(fn: Callable):
        def decorate(self, *args, **kwargs):
            if self._connected:
                return fn(self, *args, **kwargs)
            return "0"
        return decorate

    def disconnect(self) -> None:
        """ Disconnect from the scope """
        if self._connected and self._instrument:
            self._instrument.close()
        self._connected = False

    @connected
    def write(self, command: str) -> None:
        """ Write to the scope """
        self._instrument.write(command)

    @connected
    def query(self, command: str) -> str:
        """ query the scope """
        return self._instrument.query(command)

    def get_source(self):
        """ Return which channel is active """
        return int(self.query(":MEASure:SOURce?").replace("CHAN", ""))

    def get_offset(self) -> float:
        """ Return the offset """
        return float(self.query(f":CHANnel{self._channel}:OFFSet?"))

    def get_volts(self) -> float:
        """ Return the channel volts scale """
        return float(self.query(f":CHANnel{self._channel}:SCALe?"))

    def get_time(self) -> float:
        """ Return the scope time scale """
        return float(self.query(":TIMebase:SCALe?"))

    def set_source(self, channel: int = 1):
        """ Set the active channel """
        self._channel = channel
        self.write(f":MEASure:SOURce {self._channel}")

    def set_offset(self, value: float) -> None:
        """ Set the offset """
        self.write(f":CHANnel{self._channel}:OFFSet {value}")

    def set_volts(self, value: float) -> None:
        """ Set the volts """
        self.write(f":CHANnel{self._channel}:SCALe {value}V")

    def set_time(self, value: float) -> None:
        """ Set the time scale """
        self.write(f":TIMebase:SCALe {value}")

    def update(self) -> list[str]:
        """ Set the scope data """
        def result(cmd):
            x = self.query(cmd)
            try:
                x = float(x) if x else 0.0
            except ValueError as e:
                logging.error(f"{cmd}:{x} {e}")
                x = 0.01
            return x
        freq = result(':MEASure:FREQuency?')
        duty = result(':MEASure:PDUTy?')
        vavg = result(':MEASure:VAVG?')
        volt = result(':MEASure:VAMP?')
        self._data.date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self._data.freq = f"{round(freq / 1000, 2)}" if freq <= 9999 else self._data.freq
        self._data.duty = f"{round(duty * 100, 2)}%" if duty <= 9999 else self._data.duty
        self._data.vavg = f"{round(vavg, 2)}" if vavg <= 9999 else self._data.vavg
        self._data.volt = f"{round(volt, 2)}" if volt <= 9999 else self._data.volt
