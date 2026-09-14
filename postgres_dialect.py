from sql_dialect import SQLDialect

class PostgresDialect(SQLDialect):
    TYPE_MAPPING = {
        int: "INT",
        float: "REAL",
        str: "VARCHAR(255)",
        bool: "BOOLEAN"
    }

    def column_type(self, value_type) -> str:
        return self.TYPE_MAPPING.get(value_type, "TEXT")

    def primary_key_column(self, column_name: str, value_type) -> str:
        column = self.column_type(value_type)
        if column == "INT":
            return f"{column_name} SERIAL PRIMARY KEY"
        return f"{column_name} {column} PRIMARY KEY"

    def age_in_years_expression(self, column: str) -> str:
        return f"EXTRACT(YEAR FROM AVG(AGE({column}::date)))::int"

    def age_diff_expression(self, column: str) -> str:
        return f"EXTRACT(YEAR FROM MAX(AGE({column}::date)) - MIN(AGE({column}::date)))::int"