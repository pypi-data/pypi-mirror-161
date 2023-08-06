"""Library for internal helpers on test objects."""

import grpc

from rime_sdk.internal.backend import RIMEBackend
from rime_sdk.protos.test_run_results.test_run_results_pb2 import (
    GetBatchResultRequest,
    GetBatchResultResponse,
)


def get_batch_result_response(
    backend: RIMEBackend, test_run_id: str, test_type: str,
) -> GetBatchResultResponse:
    """Obtain the test batch summary response."""
    with backend.get_test_run_results_stub() as results_reader:
        req = GetBatchResultRequest(test_run_id=test_run_id, test_type=test_type)
        try:
            res: GetBatchResultResponse = results_reader.GetBatchResult(req)
            return res
        except grpc.RpcError as rpc_error:
            if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
                raise ValueError(
                    f"The test batch for {test_type} and test run "
                    f"{test_run_id} was not found."
                ) from None
            raise ValueError(rpc_error.details()) from None
