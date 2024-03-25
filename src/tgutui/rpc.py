import time
import logging
from typing import Callable
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
from jsonrpclib import Server
from tgutui.kit import Kit

class Rpc:
    """
    Remote procedure class for the Camera and Textual
    windows to communicate with each other
    """

    HOST = "localhost"

    def __init__(self, server: int, client: int):
        self._client_port = client
        self._server_port = server
        self._request: Server = None
        self._server: SimpleJSONRPCServer = None
        self._registers: list[(Callable, str)] = []
        self.running: bool = False

    def request(self, method: str, *args) -> Server | None:
        """ Make a request to a window with args """
        address = f"http://{Rpc.HOST}:{self._client_port}"
        request = Server(address)
        try:
            return getattr(request, method)(*args)
        except ConnectionRefusedError:
            logging.debug(f"Connection refused:{address}, {method}")
        return None

    def register(self, method: Callable, name: str) -> None:
        """ Register a method for a remote window to call """
        self._registers.append((method, name))

    def disconnect(self):
        """ Disconnect the RPC """
        self.running = False
        if self._server:
            self._server.shutdown()
        self._server = None

    def connect(self):
        """ Connect the RPC """
        try:
            self._server = SimpleJSONRPCServer(
                (Rpc.HOST, self._server_port),
                logRequests=Kit.LOG_RPC,
            )
        except Exception as e:
            logging.error(f"{e}")
            raise e
        for method, name in self._registers:
            self._server.register_function(method, name)
        self.running = True
        logging.info(f"RPC serving on port {self._server_port}")
        self._server.serve_forever()

    def check_started(self):
        """ Wait for the Rpc service to start """
        for _ in range(10):
            time.sleep(0.1)
            if self._server:
                break
        if not self._server:
            self.disconnect()
            msg = "Service did not start"
            logging.error(msg)
            raise RuntimeError(msg)
