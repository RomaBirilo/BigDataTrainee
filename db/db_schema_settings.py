from pydantic import BaseModel

class TableConfig(BaseModel):
    name: str
    primary_key: str

class RelationshipConfig(BaseModel):
    left_table: str
    left_field: str
    right_table: str
    right_field: str

class IndexConfig(BaseModel):
    table: str
    field: str

class DBSchemaConfig(BaseModel):
    tables: list[TableConfig]
    relationships: list[RelationshipConfig]
    indexes: list[IndexConfig]