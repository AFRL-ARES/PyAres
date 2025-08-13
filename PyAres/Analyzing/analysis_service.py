import grpc
from concurrent import futures

from ares_datamodel import ares_analysis_service_pb2
from ares_datamodel import ares_analysis_service_pb2_grpc

class AresAnalyzer(ares_analysis_service_pb2_grpc.AresAnalysisServiceServicer):
    def __init__(self, port):
        self.port = port
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        ares_analysis_service_pb2_grpc.add_AresAnalysisServiceServicer_to_server(self, self.server)
        self.server.add_insecure_port(f"localhost:{port}")


    def start(self):
        if self.server:
            self.server.start()
            print(f"Analyzer started, listening on {self.port}")
            self.server.wait_for_termination()        

    def stop(self):
        if self.server:
            self.server.stop()
            print("Planner successfully stopped.")

    def Analyze(self, request, context):
        return self.UserAnalysis(request, context)
    
    def UserAnalysis(request, context):
        """Handles incoming Analysis requests.

        Takes incoming request messages received over the gRPC service. Designed to be overwritten by the user
        to handle incoming requests with desired custom analysis logic before returning a score of the image of the print.
        This method is NOT designed to be called by the user, but by the gRPC service.

        Args:
            request: A protobuf message that contains the image property, a sequence of bytes representing the given image data.
            context: The context of the gRPC request.

        Returns:
            A copy of the PrintAnalysisResponse protobuf message containing the score for the received image. 
        """
        print("No override given for analysis call! Returning default analysis response.")
        return ares_analysis_service_pb2.analyzing_dot_analysis__pb2(score=-1)

    def __del__(self):
        #Stop the gRPC server when the object is disposed
        self.stop() 


if __name__ == "__main__":
    print("Hello World")