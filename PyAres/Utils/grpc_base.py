import grpc
from concurrent import futures
import logging
from typing import Optional

from .logging_utils import setup_logger

class AresGrpcServiceBase:
    """
    Base class for ARES gRPC services to handle server lifecycle and common configuration.
    """
    def __init__(self, 
                 service_name: str, 
                 description: str, 
                 version: str, 
                 port: int, 
                 use_localhost: bool = True, 
                 max_message_size: int = -1):
        self.service_name = service_name
        self.description = description
        self.version = version
        self._port = port
        self._logger = setup_logger(f"PyAres.{self.__class__.__name__}")

        server_options = []
        if max_message_size != -1:
            self._logger.info(f"Setting Custom Max Message Size: {max_message_size} MB")
            server_options.append(('grpc.max_receive_message_length', max_message_size * 1024 * 1024))
        
        self._server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), options=server_options)
        
        if use_localhost:
            self._server.add_insecure_port(f'localhost:{self._port}')
        else:
            self._server.add_insecure_port(f'[::]:{self._port}')

    def start(self, wait_for_termination: bool = True):
        """
        Starts the gRPC server.
        """
        self._logger.info(f"Starting {self.service_name} on port {self._port}...")
        self._server.start()
        if wait_for_termination:
            self._server.wait_for_termination()

    def stop(self):
        """
        Stops the gRPC server.
        """
        self._logger.info(f"Stopping {self.__class__.__name__}...")
        self._server.stop(0).wait()

    def get_server(self):
        return self._server