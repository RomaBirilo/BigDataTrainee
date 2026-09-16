import os
import pickle
import logging

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive"]


def get_credentials(client_secret_path: str, token_path: str):
    creds = None

    if os.path.exists(token_path):
        logger.debug("Loading cached Google token: %s", token_path)
        with open(token_path, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.debug("Refreshing expired Google token")
            creds.refresh(Request())
        else:
            logger.info("Starting Google OAuth flow — browser will open")
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, "wb") as f:
            pickle.dump(creds, f)
        logger.debug("Saved Google token: %s", token_path)

    return creds