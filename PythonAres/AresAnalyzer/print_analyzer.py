from concurrent import futures
from .messages import print_analyzer_pb2_grpc

import grpc
 

class PrintAnalyzer():
    def __init__(self, port):
        self.port = port
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        print_analyzer_pb2_grpc.add_AresPlannerGrpcServicer_to_server(self, self.server)
        self.server.add_insecure_port("localhost:" + self.port)
        #Should probably actually be wait_for_termination, but changed for testing purposes
        #server.start()

    def start(self):
        if self.server:
            self.server.wait_for_termination()        
            print("Analyzer started, listening on " + self.port)

    def stop(self):
        if self.server:
            self.server.stop()
            print("Planner successfully stopped.")

    def Plan(self, request, context):
        print("I'm the default analysis method!")

    def __del__(self):
        self.stop() #Stop the gRPC server when the object is disposed