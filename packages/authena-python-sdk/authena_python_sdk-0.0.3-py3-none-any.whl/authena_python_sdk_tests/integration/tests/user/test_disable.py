from time import sleep

from authena_python_sdk.client import Client
from authena_python_sdk.models.user import User


def test_FUNC_client_user_disable_WITH_valid_configuration_EXPECT_user_disabled(
        sdk_client: Client,
        user: User
) -> None:
    """
    Check whether the active user can be disabled.

    :param sdk_client: SDK client.
    :param user: User fixture.

    :return: No return.
    """
    # Get the created new user.
    refreshed_user = sdk_client.user.get(user.username)

    # Check that the original data exists.
    assert refreshed_user.username == user.username
    assert refreshed_user.is_active

    sdk_client.user.disable(user.username)

    # Currently, the cache is set for 10 seconds. Therefore, sleep for at least
    # 10 seconds or more (+1 second) and try get new data.
    sleep(11)

    # Refresh data from the database.
    refreshed_user = sdk_client.user.get(user.username)

    # Check that the user was indeed disabled.
    assert refreshed_user.username == user.username
    assert not refreshed_user.is_active
