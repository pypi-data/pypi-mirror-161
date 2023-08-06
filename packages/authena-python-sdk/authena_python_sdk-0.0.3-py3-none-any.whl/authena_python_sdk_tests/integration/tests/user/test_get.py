from authena_python_sdk.client import Client
from authena_python_sdk.models.user import User


def test_FUNC_client_user_get_WITH_existing_user_EXPECT_user_returned(
        sdk_client: Client,
        user: User
) -> None:
    """
    Check whether the existing user can be retrieved.

    :param sdk_client: SDK client.
    :param user: User fixture.

    :return: No return.
    """
    # Get the created new user.
    retrieved_user = sdk_client.user.get(user.username)

    # Check that the original data exists.
    assert retrieved_user.username == user.username
    assert retrieved_user.email == user.email
    assert retrieved_user.preferred_username == user.preferred_username
    assert retrieved_user.first_name == user.first_name
    assert retrieved_user.last_name == user.last_name
    assert retrieved_user.is_active
