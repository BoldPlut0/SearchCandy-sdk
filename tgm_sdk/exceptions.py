"""TGM SDK Exceptions."""


class TGMError(Exception):
    """Base exception for TGM SDK errors."""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"TGM API Error {status_code}: {detail}")


class AuthenticationError(TGMError):
    """Raised when API key is invalid or missing."""
    pass


class GraphNotFoundError(TGMError):
    """Raised when a graph is not found."""
    pass


class NodeNotFoundError(TGMError):
    """Raised when a node is not found."""
    pass
