import json

class JSONFileManager:
    @staticmethod
    def read_json_file(path: str) -> list | dict:
        try:
            with open(path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            raise Exception(f"File {path} not found!")
        except json.JSONDecodeError as error:
            raise Exception(f"Incorrect json syntaxis! Line:{error.lineno}")
        except Exception:
            raise Exception("Unknown error!")