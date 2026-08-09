from typing import Callable, Optional

import grpc

from .datamodel_version_utils import get_datamodel_metadata_header


class DatamodelVersionServerInterceptor(grpc.ServerInterceptor):
    """
    Server interceptor that ensures each RPC sends a `datamodel-version` header
    with the installed ares_datamodel version, unless the client already
    provided one in the incoming metadata.
    """

    def intercept_service(
        self,
        continuation: Callable[[grpc.HandlerCallDetails], Optional[grpc.RpcMethodHandler]],
        handler_call_details: grpc.HandlerCallDetails,
    ) -> Optional[grpc.RpcMethodHandler]:
        handler = continuation(handler_call_details)
        if handler is None:
            return None

        header_key, header_value = get_datamodel_metadata_header()

        def wrap_behavior(behavior):
            # behavior signature depends on RPC type (request, context) or (request_iter, context),
            # but the second positional argument is always the ServicerContext.
            def new_behavior(request_or_iterator, context: grpc.ServicerContext):
                # Respect existing datamodel-version if already present on the incoming metadata
                incoming_md = context.invocation_metadata() or []
                if not any(md.key == header_key for md in incoming_md):
                    # Attach header as initial metadata
                    context.send_initial_metadata(((header_key, header_value),))
                return behavior(request_or_iterator, context)

            return new_behavior

        # Rebuild the handler with wrapped behavior for each RPC type
        if handler.unary_unary:
            return grpc.unary_unary_rpc_method_handler(
                wrap_behavior(handler.unary_unary),
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )

        if handler.unary_stream:
            return grpc.unary_stream_rpc_method_handler(
                wrap_behavior(handler.unary_stream),
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )

        if handler.stream_unary:
            return grpc.stream_unary_rpc_method_handler(
                wrap_behavior(handler.stream_unary),
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )

        if handler.stream_stream:
            return grpc.stream_stream_rpc_method_handler(
                wrap_behavior(handler.stream_stream),
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )

        # If for some reason none of the above matched, return the original handler untouched
        return handler