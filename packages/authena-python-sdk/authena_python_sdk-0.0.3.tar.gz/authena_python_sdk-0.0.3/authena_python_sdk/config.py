import json
from typing import Optional

from authena_python_sdk import root


class Config:
    __PUBLIC_API_KEY = 'PUBLIC_API_URL'
    __PRIVATE_API_KEY = 'PRIVATE_API_URL'

    def __init__(
            self,
            public_api_url: str,
            private_api_url: Optional[str] = None
    ):
        self.public_api_url = public_api_url
        self.private_api_url = private_api_url

    @staticmethod
    def load() -> 'Config':
        with open(f'{root}/config.json') as file:
            data = json.loads(file.read())
        
        return Config(
            public_api_url=data[Config.__PUBLIC_API_KEY],
            private_api_url=data[Config.__PRIVATE_API_KEY]
        )
