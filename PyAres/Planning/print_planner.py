from concurrent import futures
from .messages import print_planner_pb2_grpc
from .messages import print_planner_pb2

import grpc

class PrintPlanner(print_planner_pb2_grpc.PrintPlannerGrpc):
    def __init__(self, port):
        self.port = port
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        print_planner_pb2_grpc.add_PrintPlannerGrpcServicer_to_server(self, self.server)
        self.server.add_insecure_port(f"localhost:{port}")

    def start(self):
        if self.server:
            self.server.start()
            print(f"Print planner started, listening on {self.port}")
            self.server.wait_for_termination()        

    def stop(self):
        if self.server:
            self.server.stop()
            print("Print planner successfully stopped.")

    def Plan(self, request: print_planner_pb2.PrintPlanRequest, context) -> print_planner_pb2.PrintPlanResponse:
        #Can't override this method, as it's bound to the receival of our request.
        #Call the user method which theoretically has been overridden.
        return self.DoPlanning(request, context)

    def DoPlanning(request: print_planner_pb2.PrintPlanRequest, context) -> print_planner_pb2.PrintPlanResponse:
        print("Received a print planning request, but no override for plan logic is in place!")
        print("To utilize custom planning logic, override the DoPlanning method of the AresPlanner class.")
        print("Returning an empty plan response.")
        return print_planner_pb2.PlanResponse()

    def __del__(self):
        #Stop the gRPC server when the object is disposed
        self.stop() 