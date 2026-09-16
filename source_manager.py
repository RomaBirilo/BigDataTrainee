from abc import ABC, abstractmethod

class SourceManager(ABC):
    @abstractmethod
    async def read(self, path: str) -> list | dict:
        pass

    @abstractmethod
    async def write(self, path: str, data: list | dict) -> None:
        pass