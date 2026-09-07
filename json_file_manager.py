import json
import logging

logger = logging.getLogger(__name__)

class JSONFileManager:
    @staticmethod
    def read_json_file(path: str) -> list | dict:
        logger.debug("Reading JSON file: %s", path)
        with open(path, 'r') as file:
            return json.load(file)

    @staticmethod
    def write_json_file(path: str, data: list[dict] | dict) -> None:
        logger.debug("Writing JSON file: %s", path)
        with open(path, 'w') as file:
            json.dump(data, file, indent=4)