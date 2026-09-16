from db.dialects.sql_dialect import SQLDialect

class MySQLDialect(SQLDialect):
    TYPE_MAPPING = {
        int: "INT",
        float: "DOUBLE",
        str: "VARCHAR(255)",
        bool: "BOOLEAN"
    }

    def column_type(self, value_type) -> str:
        return self.TYPE_MAPPING.get(value_type, "TEXT")

    def primary_key_column(self, column_name: str, value_type) -> str:
        column = self.column_type(value_type)
        if column == "INT":
            return f"{column_name} INT PRIMARY KEY"
        return f"{column_name} {column} PRIMARY KEY"

    def age_in_years_expression(self, column: str) -> str:
        date_expr = f"STR_TO_DATE(LEFT({column}, 10), '%Y-%m-%d')"
        return f"CAST(AVG(TIMESTAMPDIFF(YEAR, {date_expr}, CURDATE())) AS SIGNED)"

    def age_diff_expression(self, column: str) -> str:
        date_expr = f"STR_TO_DATE(LEFT({column}, 10), '%Y-%m-%d')"
        return f"CAST(TIMESTAMPDIFF(YEAR, MIN({date_expr}), MAX({date_expr})) AS SIGNED)"