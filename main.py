from JSONFileManager import JSONFileManager
from PostgresConnectionManager import PostgresConnectionManager
from PostgresSchemaManager import PostgresSchemaManager
from QueryManager import QueryManager

conn_params = {
    "host": "localhost",
    "database": "trainee_python_practice",
    "user": "postgres",
    "password": "1234",
    "port": "5432"
}
db_connection = PostgresConnectionManager(conn_params)
try:
    print("Try to connect...")
    db_connection.connect()
    print("Connection successfully!")

    print("Reading files...")
    rooms_data = JSONFileManager.read_json_file("rooms.json")
    students_data = JSONFileManager.read_json_file("students.json")
    print("Files were read successfully!")

    schema_manager = PostgresSchemaManager(connection_manager=db_connection)

    print("Creating schema...")
    schema_manager.create_table("rooms", rooms_data[0], "id")
    print("Table was created successfully!")
    schema_manager.insert_data("rooms", rooms_data)
    print("Data was inserted successfully!")

    schema_manager.create_table("students", students_data[0], "id")
    print("Table was created successfully!")
    schema_manager.insert_data("students", students_data)
    print("Data was inserted successfully!")

    schema_manager.create_relationship("students", "room",
                                       "rooms", "id")
    print("Relationship was created successfully!")

    schema_manager.create_index("rooms", "name")
    print("Index was created successfully!")
    schema_manager.create_index("students", "name")
    print("Index was created successfully!")
    schema_manager.create_index("students", "birthday")
    print("Index was created successfully!")
    print("Schema was created successfully!")

    query_manager = QueryManager(connection_manager=db_connection)

    print("Queries execution...")
    response = query_manager.rooms_with_students_number()
    JSONFileManager.write_json_file("rooms_with_students_number.json", response)

    response = query_manager.rooms_with_smallest_avg_age()
    JSONFileManager.write_json_file("rooms_with_smallest_avg_age.json", response)

    response = query_manager.rooms_with_largest_age_diff()
    JSONFileManager.write_json_file("rooms_with_largest_age_diff.json", response)

    response = query_manager.rooms_with_diff_sex_students()
    JSONFileManager.write_json_file("rooms_with_diff_sex_students.json", response)
    print("All queries were executed successfully!")

except Exception as error:
    print(error)
finally:
    db_connection.close()