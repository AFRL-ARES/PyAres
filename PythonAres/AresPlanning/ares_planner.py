from concurrent import futures
from .messages import ares_planner_pb2_grpc
from .messages import ares_planner_pb2

import grpc

class AresPlanner(ares_planner_pb2_grpc.AresPlannerGrpc):
    def __init__(self, port):
        self.port = port
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        ares_planner_pb2_grpc.add_AresPlannerGrpcServicer_to_server(self, self.server)
        self.server.add_insecure_port(f"localhost:{port}")

    def start(self):
        if self.server:
            self.server.start()
            print(f"Planner started, listening on {self.port}")
            self.server.wait_for_termination()        

    def stop(self):
        if self.server:
            self.server.stop()
            print("Planner successfully stopped.")

    def Plan(self, request, context):
        return self.DoPlanning(request, context)
        #Run Planning Service

    def DoPlanning(request, context):
        print("Received a planning request, but no override for plan logic is in place!")
        print("To utilize custom planning logic, override the DoPlanning method of the AresPlanner class.")
        print("Returning an empty plan response.")
        return ares_planner_pb2.PlanResponse()

    def __del__(self):
        #Stop the gRPC server when the object is disposed
        self.stop() 