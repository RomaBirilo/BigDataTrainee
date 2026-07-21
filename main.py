from DataOperatorPostgres import DataOperatorPostgres

conn_params = {
    "host": "localhost",
    "database": "trainee_python_practice",
    "user": "postgres",
    "password": "1234",
    "port": "5432"
}
data_operator = DataOperatorPostgres(conn_params)

try:
    data_operator.connect()

    data_operator.read_json_file("rooms.json")
    data_operator.create_table("rooms", "id")
    data_operator.insert_data("rooms")

    data_operator.read_json_file("students.json")
    data_operator.create_table("students", "id")
    data_operator.insert_data("students")

    data_operator.create_relationship("students", "room",
                                      "rooms", "id")
except Exception as error:
    print(error)
finally:
    data_operator.close()