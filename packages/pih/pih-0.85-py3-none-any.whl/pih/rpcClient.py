from typing import Dict
import grpc
import rpcCommandCall_pb2_grpc as pb2_grpc
import rpcCommandCall_pb2 as pb2


class rpcCommandClient():

    def __init__(self):
        self.host = "orion"
        self.server_port = 50051
        self.channel = grpc.insecure_channel(f"{self.host}:{self.server_port}")
        self.stub = pb2_grpc.UnaryStub(self.channel)

    def call_command(self, name: str, parameters: Dict = None):
        return self.stub.rpcCallCommand(pb2.rpcCommand(name=name, parameters=parameters))


if __name__ == '__main__':
    result = rpcCommandClient().call_command("ping")
    print(f'{result}')
