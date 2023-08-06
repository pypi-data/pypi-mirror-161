import random

# noinspection PyUnresolvedReferences
import pytest

# Import all fixtures.
# noinspection PyUnresolvedReferences
from authena_python_sdk_tests.integration.fixtures import *


# Force all tests to reseed before running.
@pytest.fixture(scope='function', autouse=True)
def faker_seed():
    return random.random()


# Force all tests use a known locale.
@pytest.fixture(scope='session', autouse=True)
def faker_session_locale():
    return ['lt_LT']
