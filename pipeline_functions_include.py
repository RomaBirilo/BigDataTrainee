import asyncio
import logging
import time

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

async def _producer(batches: AsyncIterator[list[dict]], queue: asyncio.Queue, table_name: str) -> None:
    logger.debug("[%s] producer: started", table_name)
    batch_no = 0
    t_prev = time.perf_counter()

    async for batch in batches:
        batch_no += 1
        built = time.perf_counter() - t_prev
        logger.debug("[%s] producer: batch #%d ready (%d rows, took %.2fs), queue size=%d",
                     table_name, batch_no, len(batch), built, queue.qsize())

        t0 = time.perf_counter()
        await queue.put(batch)
        waited = time.perf_counter() - t0
        if waited > 0.05:
            logger.debug("[%s] producer: batch #%d put after waiting %.2fs (queue was full)",
                         table_name, batch_no, waited)
        t_prev = time.perf_counter()

    await queue.put(None)
    logger.debug("[%s] producer: finished, %d batches, stop signal sent", table_name, batch_no)

async def _consumer(schema_manager: SchemaManager, table_name: str, primary_key: str,
                    queue: asyncio.Queue, transform) -> None:
    logger.debug("[%s] consumer: started", table_name)
    table_created = False
    batch_no = 0

    while True:
        t0 = time.perf_counter()
        batch = await queue.get()
        if batch:
            transform(batch)
        waited = time.perf_counter() - t0

        if batch is None:
            logger.debug("[%s] consumer: stop signal received", table_name)
            break

        batch_no += 1
        if waited > 0.05:
            logger.debug("[%s] consumer: batch #%d received after waiting %.2fs (queue was empty)",
                         table_name, batch_no, waited)

        if not table_created:
            logger.debug("[%s] consumer: creating table on first batch", table_name)
            await schema_manager.create_table(table_name, batch[0], primary_key)
            table_created = True

        t0 = time.perf_counter()
        await schema_manager.insert_data(table_name, batch)
        logger.debug("[%s] consumer: batch #%d inserted in %.2fs, queue size=%d",
                     table_name, batch_no, time.perf_counter() - t0, queue.qsize())


async def fill_table_stream(schema_manager: SchemaManager, source_manager: SourceManager,
                             table: TableConfig, transform, batch_size: int = 10_000) -> None:
    logger.info("Streaming data into table %s", table.name)
    stream = source_manager.read_stream(f"{table.name}.json")
    batches = batched(stream, batch_size)
    queue: asyncio.Queue = asyncio.Queue(maxsize=2)

    await asyncio.gather(
        _producer(batches, queue, table.name),
        _consumer(schema_manager, table.name, table.primary_key, queue, transform),
    )
    logger.info("Finished streaming data into table %s", table.name)