import abc
from typing import Any


class AbstractServiceConnexion(abc.ABC):
    @abc.abstractmethod
    def get(self, path: str, params: dict = None, stream=False):
        pass

    @abc.abstractmethod
    def xget(self, path: str, data: dict = None, params: dict = None, stream=False):
        pass

    @abc.abstractmethod
    def post(
        self, path: str, data: dict = None, params: dict = None, files: Any = None
    ):
        pass

    @abc.abstractmethod
    def patch(self, path: str, data: dict = None, params: dict = None):
        pass

    @abc.abstractmethod
    def put(self, path: str, data: dict = None, params: dict = None):
        pass

    @abc.abstractmethod
    def delete(self, path: str, data: dict = None, params: dict = None):
        pass
