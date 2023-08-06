from typing import List


class NetworkError(Exception):
    """Raised when an HTTPError occurs."""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class UnauthorizedError(Exception):
    """Raised when user is not authorized."""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class MockResponseNotDefinedError(Exception):
    """Raised when response is not defined in MockServiceConnexion"""

    def __init__(self, method: str, path: str, known_paths: List[str]) -> None:
        self.method = method
        self.path = path
        self.known_paths = known_paths
