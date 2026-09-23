import asyncio
import logging

from db.schema_manager import SchemaManager
from data_sources.source_manager import SourceManager
from db.db_schema_settings import TableConfig
from typing import AsyncIterator

logger = logging.getLogger(__name__)

async def batched(records: AsyncIterator[dict], batch_size: int) -> AsyncIterator[list[dict]]:
    batch = []
    async for record in records:
        batch.append(record)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch

async def _producer(batches: AsyncIterator[list[dict]], queue: asyncio.Queue) -> None:
    async for batch in batches:
        await queue.put(batch)
    await queue.put(None)


async def _consumer(schema_manager: SchemaManager, table_name: str, primary_key: str,
                     queue: asyncio.Queue) -> None:
    table_created = False
    while True:
        batch = await queue.get()
        if batch is None:
            break
        if not table_created:
            await schema_manager.create_table(table_name, batch[0], primary_key)
            table_created = True
        await schema_manager.insert_data(table_name, batch)


async def fill_table_stream(schema_manager: SchemaManager, source_manager: SourceManager,
                             table: TableConfig, batch_size: int = 10_000) -> None:
    logger.info("Streaming data into table %s", table.name)
    stream = source_manager.read_stream(f"{table.name}.json")
    batches = batched(stream, batch_size)
    queue: asyncio.Queue = asyncio.Queue(maxsize=2)

    await asyncio.gather(
        _producer(batches, queue),
        _consumer(schema_manager, table.name, table.primary_key, queue),
    )
    logger.info("Finished streaming data into table %s", table.name)