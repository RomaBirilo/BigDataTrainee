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
    print("Connection success!")
except Exception as error:
    print(error)
finally:
    data_operator.close()