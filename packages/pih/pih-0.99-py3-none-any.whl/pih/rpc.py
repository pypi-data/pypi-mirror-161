from dataclasses import dataclass
from typing import Callable
import grpc

from concurrent import futures

import pih.rpcCommandCall_pb2_grpc as pb2_grpc
import pih.rpcCommandCall_pb2 as pb2
from pih.tools import DataTools


@dataclass
class rpcCommand:
    host: str
    port: int
    name: str


class RPC:

    class UnaryService(pb2_grpc.UnaryServicer):

        def __init__(self, handler: Callable, *args, **kwargs):
            self.handler = handler

        def rpcCallCommand(self, command, context):
            parameters = command.parameters
            if parameters is not None and parameters != "":
                parameters = DataTools.rpc_unrepresent(parameters)
            return pb2.rpcCommandResult(data=DataTools.represent(self.handler(command.name, parameters, context)))

    class Server:

        @staticmethod
        def serve(host_name: str, port: int, handler: Callable):
            from pih.pih import PIH
            PIH.VISUAL.SHOW_SERVER_HEADER(host_name)
            server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
            pb2_grpc.add_UnaryServicer_to_server(
                RPC.UnaryService(handler), server)
            server.add_insecure_port(f"{host_name}:{port}")
            server.start()
            server.wait_for_termination()

    class rpcCommandClient():

        def __init__(self, host: str, port: int):
            self.host = host
            self.server_port = port
            self.channel = grpc.insecure_channel(
                f"{self.host}:{self.server_port}")
            self.stub = pb2_grpc.UnaryStub(self.channel)

        def call_command(self, name: str, parameters: dict = None):
            return self.stub.rpcCallCommand(pb2.rpcCommand(name=name, parameters=parameters))

    @staticmethod
    def call(command: rpcCommand, parameters: dict = None) -> str:
        return RPC.rpcCommandClient(command.host, command.port).call_command(command.name,  DataTools.rpc_represent(parameters)).data