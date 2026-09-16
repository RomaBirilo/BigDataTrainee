from abc import ABC, abstractmethod

class SQLDialect(ABC):
    @abstractmethod
    def column_type(self, value_type) -> str:
        pass

    @abstractmethod
    def primary_key_column(self, column_name: str, value_type) -> str:
        pass

    @abstractmethod
    def age_in_years_expression(self, column: str) -> str:
        pass

    @abstractmethod
    def age_diff_expression(self, column: str) -> str:
        pass