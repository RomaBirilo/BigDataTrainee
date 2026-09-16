import asyncio
import io
import json
import logging

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

from data_sources.source_manager import SourceManager
from data_sources.google_auth import get_credentials

logger = logging.getLogger(__name__)

class GoogleDriveFileManager(SourceManager):
    def __init__(self, client_secret_path: str, token_path: str, folder_id: str | None = None) -> None:
        self.client_secret_path = client_secret_path
        self.token_path = token_path
        self.folder_id = folder_id
        self._service = None

    def _get_service(self):
        if self._service is None:
            creds = get_credentials(self.client_secret_path, self.token_path)
            self._service = build("drive", "v3", credentials=creds)
        return self._service

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