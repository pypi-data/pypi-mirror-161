"""Internal library of client-side gRPC interceptors."""
from typing import Any, NamedTuple, Optional, Sequence, Tuple, Union

import grpc


class ClientCallDetails(NamedTuple):
    """Defines the fields in the named tuple type in grpc._ClientCallDetails."""

    method: str
    timeout: Optional[float]
    metadata: Optional[Sequence[Tuple[str, Union[str, bytes]]]]
    credentials: Optional[grpc.CallCredentials]
    wait_for_ready: Optional[bool]
    compression: Any  # Type added in grpcio 1.23.0


def _create_new_details_with_metadata(
    client_call_details: grpc.ClientCallDetails,
) -> ClientCallDetails:
    metadata = []
    if client_call_details.metadata is not None:
        metadata = list(client_call_details.metadata)
    metadata.append(("client-type", "sdk",))
    new_details = ClientCallDetails(
        client_call_details.method,
        client_call_details.timeout,
        metadata,
        client_call_details.credentials,
        client_call_details.wait_for_ready,
        client_call_details.compression,
    )
    return new_details


class AddMetadataUnaryUnaryClientInterceptor(grpc.UnaryUnaryClientInterceptor):
    """UnaryUnaryClientInterceptor to add (client-type = sdk) metadata to all SDK gRPC calls."""

    def __init__(self) -> None:
        """Create an AddMetadataUnaryUnaryClientInterceptor."""

    def intercept_unary_unary(
        self,
        continuation: Any,
        client_call_details: grpc.ClientCallDetails,
        request: Any,
    ) -> Any:
        """Intercept a unary-unary invocation asynchronously. Override from grpc.UnaryUnaryClientInterceptor."""
        return continuation(
            _create_new_details_with_metadata(client_call_details), request
        )


class AddMetadataUnaryStreamClientInterceptor(grpc.UnaryStreamClientInterceptor):
    """UnaryStreamClientInterceptor to add (client-type = sdk) metadata to all SDK gRPC calls."""

    def __init__(self) -> None:
        """Create an AddMetadataUnaryStreamClientInterceptor."""

    def intercept_unary_stream(
        self,
        continuation: Any,
        client_call_details: grpc.ClientCallDetails,
        request: Any,
    ) -> Any:
        """Intercept a unary-stream invocation asynchronously. Override from grpc.UnaryStreamClientInterceptor."""
        return continuation(
            _create_new_details_with_metadata(client_call_details), request
        )
