from dataclasses import dataclass
from typing import Callable
import grpc

from concurrent import futures
from build.lib.pih.pih import PIH

import pih.rpcCommandCall_pb2_grpc as pb2_grpc
import pih.rpcCommandCall_pb2 as pb2
from pih.const import HOST_COLLECTION, RPC_CONST
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

    class ORION:

        @staticmethod
        def create_rpc_command(command_name: str) -> rpcCommand:
            return rpcCommand(HOST_COLLECTION.ORION.HOST_NAME(), RPC_CONST.PORT(), command_name)

        @staticmethod
        def get_free_marks() -> str:
            d = RPC.call(RPC.ORION.create_rpc_command("get_free_marks"))
            return d

        @staticmethod
        def get_mark_by_tab_number(value: str) -> dict:
            return RPC.call(RPC.ORION.create_rpc_command("get_mark_by_tab_number"), value)

        @staticmethod
        def get_mark_by_person_name(value: str) -> dict:
            return RPC.call(RPC.ORION.create_rpc_command("get_mark_by_person_name"), value)

        @staticmethod
        def get_free_marks_group_statistics() -> str:
            return RPC.call(RPC.ORION.create_rpc_command("get_free_marks_group_statistics"))

        @staticmethod
        def get_free_marks_by_group(group: dict) -> str:
            return RPC.call(RPC.ORION.create_rpc_command("get_free_marks_by_group"), group)

    class AD:

        @staticmethod
        def create_rpc_command(command_name: str) -> rpcCommand:
            return rpcCommand(HOST_COLLECTION.AD.HOST_NAME(), RPC_CONST.PORT(), command_name)

        @staticmethod
        def user_is_exsits_by_login(value: str) -> str:
            return RPC.call(RPC.AD.create_rpc_command("user_is_exsits_by_login"), value)
