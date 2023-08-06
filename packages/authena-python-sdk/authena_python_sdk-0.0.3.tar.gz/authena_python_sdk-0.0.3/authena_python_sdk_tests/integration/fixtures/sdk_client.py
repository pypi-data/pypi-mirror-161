import os

import pytest

from authena_python_sdk.client import Client
from authena_python_sdk.config import Config

AUTHENA_PUBLIC_API_URL = os.environ['AUTHENA_PUBLIC_API_URL']
AUTHENA_API_KEY = os.environ['AUTHENA_API_KEY']
AUTHENA_API_SECRET = os.environ['AUTHENA_API_SECRET']

assert AUTHENA_PUBLIC_API_URL is not None
assert len(AUTHENA_PUBLIC_API_URL)

assert AUTHENA_API_KEY is not None
assert len(AUTHENA_API_KEY)

assert AUTHENA_API_SECRET is not None
assert len(AUTHENA_API_SECRET)


@pytest.fixture(scope='session')
def sdk_client() -> Client:
    return Client(
        api_key=AUTHENA_API_KEY,
        api_secret=AUTHENA_API_SECRET,
        config=Config(
            public_api_url=AUTHENA_PUBLIC_API_URL
        )
    )
