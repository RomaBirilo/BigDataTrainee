import json

class JSONFileManager:
    @staticmethod
    def read_json_file(path: str) -> list | dict:
            with open(path, 'r') as file:
                return json.load(file)

    @staticmethod
    def write_json_file(path: str, data: list[dict] | dict) -> None:
        try:
            with open(path, 'w') as file:
                json.dump(data, file, indent=4)
        except FileNotFoundError:
            raise Exception(f"Failed to create the file {path}!")
        except TypeError as error:
            raise Exception(f"Incorrect json syntaxis!{error}")
        except Exception:
            raise Exception("Unknown error!")