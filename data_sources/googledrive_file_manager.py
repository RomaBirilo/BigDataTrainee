import asyncio
import io
import json
import logging
from typing import AsyncIterator

import aiohttp
import ijson
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

from data_sources.source_manager import SourceManager
from data_sources.google_auth import get_credentials

logger = logging.getLogger(__name__)

DRIVE_DOWNLOAD_URL = "https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
CHUNK_SIZE = 256 * 1024

class AsyncByteStreamReader:
    def __init__(self, chunk_iterator: AsyncIterator[bytes]) -> None:
        self._chunk_iterator = chunk_iterator
        self._buffer = b""
        self._exhausted = False

    async def read(self, size: int = -1) -> bytes:
        while not self._exhausted and (size < 0 or len(self._buffer) < size):
            try:
                chunk = await self._chunk_iterator.__anext__()
                self._buffer += chunk
            except StopAsyncIteration:
                self._exhausted = True
                break

        if size < 0:
            result, self._buffer = self._buffer, b""
        else:
            result, self._buffer = self._buffer[:size], self._buffer[size:]

        return result

class GoogleDriveFileManager(SourceManager):
    def __init__(self, client_secret_path: str, token_path: str, folder_id: str | None = None) -> None:
        self.client_secret_path = client_secret_path
        self.token_path = token_path
        self.folder_id = folder_id
        self._service = None
        self._credentials = None

    def _get_service(self):
        if self._service is None:
            self._service = build("drive", "v3", credentials=self._get_credentials())
        return self._service

    def _get_credentials(self):
        if self._credentials is None:
            self._credentials = get_credentials(self.client_secret_path, self.token_path)
        return self._credentials

    def _find_file_id(self, filename: str) -> str | None:
        service = self._get_service()
        query_parts = [f"name = '{filename}'", "trashed = false"]
        if self.folder_id:
            query_parts.append(f"'{self.folder_id}' in parents")
        query = " and ".join(query_parts)

        results = service.files().list(
            q=query, fields="files(id, name)", pageSize=1
        ).execute()

        files = results.get("files", [{}])
        return files[0].get("id")

    async def read(self, path: str) -> list | dict:
        return await asyncio.to_thread(self._read_sync, path)

    def _read_sync(self, path: str) -> list | dict:
        logger.debug("Reading from Google Drive: %s", path)
        service = self._get_service()

        file_id = self._find_file_id(path)
        if file_id is None:
            raise FileNotFoundError(f"File not found on Google Drive: {path}")

        request = service.files().get_media(fileId=file_id)
        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request)

        done = False
        while not done:
            _, done = downloader.next_chunk()

        buffer.seek(0)
        return json.loads(buffer.read().decode("utf-8"))

    async def write(self, path: str, data: list | dict) -> None:
        await asyncio.to_thread(self._write_sync, path, data)

    def _write_sync(self, path: str, data: list | dict) -> None:
        logger.debug("Writing to Google Drive: %s", path)
        service = self._get_service()

        content = json.dumps(data, indent=4).encode("utf-8")
        buffer = io.BytesIO(content)
        media = MediaIoBaseUpload(buffer, mimetype="application/json", resumable=False)

        existing_file_id = self._find_file_id(path)

        if existing_file_id:
            service.files().update(fileId=existing_file_id, media_body=media).execute()
        else:
            file_metadata = {"name": path}
            if self.folder_id:
                file_metadata["parents"] = [self.folder_id]
            service.files().create(body=file_metadata, media_body=media, fields="id").execute()

    async def read_stream(self, path: str) -> AsyncIterator[dict]:
        file_id = await asyncio.to_thread(self._find_file_id, path)
        if file_id is None:
            raise FileNotFoundError(f"File not found on Google Drive: {path}")

        logger.debug("Streaming from Google Drive: %s (file_id=%s)", path, file_id)
        async for record in self._parse_stream(self._byte_stream(file_id)):
            yield record

    async def _byte_stream(self, file_id: str) -> AsyncIterator[bytes]:
        credentials = await asyncio.to_thread(self._refresh_credentials_if_needed)
        url = DRIVE_DOWNLOAD_URL.format(file_id=file_id)
        headers = {"Authorization": f"Bearer {credentials.token}"}
        timeout = aiohttp.ClientTimeout(total=None, sock_read=60, sock_connect=30)

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                async for chunk in response.content.iter_chunked(CHUNK_SIZE):
                    yield chunk

    def _refresh_credentials_if_needed(self):
        creds = self._get_credentials()
        if not creds.valid:
            creds.refresh(Request())
        return creds

    async def _parse_stream(self, byte_chunks: AsyncIterator[bytes]) -> AsyncIterator[dict]:
        reader = AsyncByteStreamReader(byte_chunks)
        async for record in ijson.items_async(reader, "item"):
            yield record