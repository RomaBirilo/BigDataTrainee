import json
import logging
from data_sources.source_manager import SourceManager
import ijson
import asyncio

logger = logging.getLogger(__name__)

class JSONFileManager(SourceManager):
    async def read(self, path: str) -> list | dict:
        logger.debug("Reading JSON file: %s", path)
        with open(path, 'r') as file:
            return json.load(file)

    async def write(self, path: str, data: list[dict] | dict) -> None:
        logger.debug("Writing JSON file: %s", path)
        with open(path, 'w') as file:
            json.dump(data, file, indent=4)

    async def read_stream(self, path: str):
        logger.debug("Streaming JSON file: %s", path)

        def sync_gen():
            with open(path, "rb") as f:
                yield from ijson.items(f, "item")

        for i, record in enumerate(sync_gen()):
            yield record
            if i % 1000 == 0:
                await asyncio.sleep(0)