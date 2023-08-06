from typing import Optional

from authena_python_sdk.client_group import ClientGroup
from authena_python_sdk.client_user import ClientUser
from authena_python_sdk.config import Config


class Client:
    def __init__(
            self,
            api_key: str,
            api_secret: str,
            config: Optional[Config] = None
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.config = config

    @property
    def group(self) -> ClientGroup:
        return ClientGroup(self.api_key, self.api_secret, self.config)

    @property
    def user(self) -> ClientUser:
        return ClientUser(self.api_key, self.api_secret, self.config)
