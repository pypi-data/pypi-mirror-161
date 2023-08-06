from time import sleep

import pytest
from b_lambda_layer_common.exceptions.container.not_found_error import NotFoundError

from authena_python_sdk.client import Client
from authena_python_sdk.models.user import User


def test_FUNC_client_user_delete_WITH_existing_user_EXPECT_user_deleted(
        sdk_client: Client,
        user: User
) -> None:
    """
    Test whether an existing user can be correctly deleted.

    :param sdk_client: Authena SDK client fixture.
    :param user: User fixture.

    :return: No return.
    """
    # Ensure user exists.
    refreshed_user = sdk_client.user.get(user.username)
    assert refreshed_user.username == user.username

    # Expect this to succeed.
    sdk_client.user.delete(user.username)

    # Currently the cache is set for 10 seconds. Therefore, sleep for at least
    # 10 seconds or more (+1 second) and try get fresh data.
    sleep(11)

    # Expect this to fail.
    with pytest.raises(NotFoundError):
        sdk_client.user.get(user.username)
