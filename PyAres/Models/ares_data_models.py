from ares_datamodel import request_metadata_pb2
from enum import Enum

class AresDataType(Enum):
    UNKNOWN = 0
    NULL = 1
    BOOLEAN = 2
    STRING = 3
    NUMBER = 4
    STRING_ARRAY = 5
    NUMBER_ARRAY = 6
    BYTE_ARRAY = 7
    BOOL_ARRAY = 8

class Outcome(Enum):
    UNSPECIFIED_OUTCOME = 0
    SUCCESS = 1
    FAILURE = 2
    WARNING = 3
    CANCELED = 4

class RequestMetadata():
    def __init__(self, proto_metadata: request_metadata_pb2.RequestMetadata):
        self.system_name = proto_metadata.system_name
        self.campaign_name = proto_metadata.campaign_name
        self.campaign_id = proto_metadata.campaign_id
        self.experiment_id = proto_metadata.experiment_id  