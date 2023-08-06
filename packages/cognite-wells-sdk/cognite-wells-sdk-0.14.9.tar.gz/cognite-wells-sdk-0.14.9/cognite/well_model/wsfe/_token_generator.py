import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

from cognite.well_model.client.utils._token_generator import TokenGenerator

log = logging.getLogger(__name__)


class EarlyRefreshTokenGenerator:
    def __init__(self):
        self.token_client_id: Optional[str] = os.getenv("COGNITE_CLIENT_ID")
        self.token_client_secret: Optional[str] = os.getenv("COGNITE_CLIENT_SECRET")
        self.token_url: Optional[str] = os.getenv("COGNITE_TOKEN_URL")
        self.token_scopes = os.getenv("COGNITE_TOKEN_SCOPES", "").split(",")
        self.token_custom_args: Dict[str, str] = {}

        self.token_generator = TokenGenerator(
            self.token_url,
            self.token_client_id,
            self.token_client_secret,
            self.token_scopes,
            self.token_custom_args,
        )

    def return_access_token(self) -> str:
        # Assumes that the WSFE will complete a request within this time.
        time_margin = timedelta(minutes=15)

        token_expire_time = datetime.fromtimestamp(self.token_generator._access_token_expires_at)

        # This is now the maximum token expiray. It leaves some extra time if
        # the WSFE uses some time to complete the next request.
        expire_time_with_margin = token_expire_time - time_margin

        if expire_time_with_margin < datetime.now():
            time_left = expire_time_with_margin - datetime.now()
            log.info(f"Generting new token since the current one experes in {time_left}")
            self.token_generator._generate_access_token()
        token: str = self.token_generator._access_token
        return token
