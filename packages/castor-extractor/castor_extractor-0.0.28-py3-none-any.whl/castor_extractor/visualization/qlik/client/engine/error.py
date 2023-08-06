from .constants import ACCESS_DENIED_ERROR_CODE, BASE_ERROR_MESSAGE


class JsonRpcError(Exception):
    """
    Error class to be raised when a JSON-RPC call response is an error
    """

    def __init__(self, message: dict, error: dict):
        self.message = message
        self.error = error
        error_message = BASE_ERROR_MESSAGE.format(message=message, error=error)
        super().__init__(error_message)

    @property
    def is_access_denied(self) -> bool:
        """
        Returns True when the error was due to Access Denied
        """
        return self.error["code"] == ACCESS_DENIED_ERROR_CODE


def raise_for_error(message: dict, response: dict) -> None:
    """Raises JsonRpcError when response is an error"""
    if "error" in response:
        raise JsonRpcError(message, response["error"])
