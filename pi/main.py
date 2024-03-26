"""
This file is intended to be run on the Raspberry Pi zero 
with the rpi_hardware_pwm and jsonrpclib-pelix packages installed.
The "dtoverlay=pwm-2chan" or "dtoverlay=pwm-2chan,pin=12,func=4,pin2=13,func2=4"
also have to be set in the /boot/config.txt file.

It is a simple JSON-RPC server that listens for duty cycle changes 
and updates the PWM signal accordingly.
"""

import time
from threading import Thread
from rpi_hardware_pwm import HardwarePWM
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer

class PiPwm: 
    def __init__(self):
        self._port = 34962
        self._ip = '0.0.0.0'
        self._running = False
        self._server: SimpleJSONRPCServer = None
        self._pwm = HardwarePWM(pwm_channel=0, hz=1000, chip=0)
        self._thread: Thread = None
    
    def start(self):
        self._server = SimpleJSONRPCServer(
            (self._ip, self._port),
            logRequests=True,
        )
        self._thread = Thread(target=self._server.serve_forever, daemon=True)
        self._server.register_function(self.change_duty)
        self._server.register_function(self.change_frequency)
        self._server.register_function(self.stop)
        self._running = True
        self._thread.start()
        self._pwm.start(10)

    def change_duty(self, duty: int):
        print(f"Changing duty cycle to {duty}")
        self._pwm.change_duty_cycle(duty)

    def change_frequency(self, freq: int):
        print(f"Changing duty frequency to {freq * 1000}Hertz")
        self._pwm.change_frequency(freq*1000)

    def stop(self):
        self._running = False
        self._server.shutdown()
        time.sleep(0.2)
        self._thread.join()

    def run(self):
        print("Listening for duty cycle changes...")
        while self._running:
            time.sleep(1)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *_):
        self.stop()


if __name__ == "__main__":
    try:
        with PiPwm() as p:
            p.run()
    except (KeyboardInterrupt, Exception) as e:
        raise e
        

         