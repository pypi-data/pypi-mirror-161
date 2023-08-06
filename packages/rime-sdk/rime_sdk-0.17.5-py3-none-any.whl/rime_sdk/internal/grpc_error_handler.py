"""Context manager to handle GRPC errors."""
from types import TracebackType
from typing import Optional, Type

import grpc


class GRPCErrorHandler:
    """Class that can be used as a context manager.

    Used so that we handle GRPC errors in a uniform way in the code base.
    """

    def __enter__(self) -> None:
        """Needed for context manager usage."""

    def __exit__(  # pylint: disable=useless-return
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        """Handle exceptions in custom way on exit."""
        # Check if an exception was raised.
        if exc_type is not None:
            # For GRPC errors, we only raise the details.
            if isinstance(exc, grpc.RpcError):
                raise ValueError(exc.details()) from None
        # Returning None will raise any other error messages as they were.
        return None
