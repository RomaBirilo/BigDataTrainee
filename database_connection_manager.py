from abc import ABC, abstractmethod

class DatabaseConnectionManager(ABC):
    @abstractmethod
    async def connect(self) -> None:
        pass

    @abstractmethod
    async def execute_query(self, query: str, params: tuple | list = None, fetch: bool = False) -> list | None:
        pass

    @abstractmethod
    async def execute_many(self, query: str, data: list[tuple]) -> None:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass