from faker import Faker

from authena_python_sdk.client import Client
from authena_python_sdk.models.group import Group


def test_FUNC_client_user_confirm_WITH_valid_configuration_EXPECT_challenge_succeeded_token_returned(
        sdk_client: Client,
        group: Group,
        faker: Faker
):
    """
    Check whether newly created user can be confirmed and access token received.

    :param sdk_client: Authena SDK client fixture.
    :param group: Group fixture.
    :param faker: Faker fixture.

    :return: No return.
    """
    # Firstly, create a user.
    user = sdk_client.user.create(
        email=faker.email(),
        preferred_username=faker.user_name(),
        first_name=faker.first_name(),
        last_name=faker.last_name()
    )
    new_password = 'Welcome2Biomapas!'

    # Try to confirm newly created user.
    sdk_client.user.confirm(
        username=user.username,
        tmp_password=user.tmp_password,
        new_password=new_password
    )

    token = sdk_client.user.create_token(
        username=user.username,
        password=new_password
    )

    # Check that tokens were created successfully.
    assert token.access_token is not None
    assert token.id_token is not None
    assert token.access_token is not None
    assert token.refresh_token is not None

    # Cleanup.
    sdk_client.user.delete(user.username)
