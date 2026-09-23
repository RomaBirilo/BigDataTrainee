from abc import ABC, abstractmethod
from typing import AsyncIterator


class SourceManager(ABC):
    @abstractmethod
    async def read(self, path: str) -> list | dict:
        pass

    @abstractmethod
    async def write(self, path: str, data: list | dict) -> None:
        pass

    @abstractmethod
    def read_stream(self, path: str) -> AsyncIterator[dict]:
        pass