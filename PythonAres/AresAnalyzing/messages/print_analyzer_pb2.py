# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: print_analyzer.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'print_analyzer.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x14print_analyzer.proto\"\x1d\n\x0c\x41nalyzePrint\x12\r\n\x05image\x18\x01 \x01(\x0c\"&\n\x15PrintAnalysisResponse\x12\r\n\x05value\x18\x01 \x01(\x01\x32H\n\x14PrintingAnalyzerGrpc\x12\x30\n\x07\x41nalyze\x12\r.AnalyzePrint\x1a\x16.PrintAnalysisResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'print_analyzer_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_ANALYZEPRINT']._serialized_start=24
  _globals['_ANALYZEPRINT']._serialized_end=53
  _globals['_PRINTANALYSISRESPONSE']._serialized_start=55
  _globals['_PRINTANALYSISRESPONSE']._serialized_end=93
  _globals['_PRINTINGANALYZERGRPC']._serialized_start=95
  _globals['_PRINTINGANALYZERGRPC']._serialized_end=167
# @@protoc_insertion_point(module_scope)
