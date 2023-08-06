import time

from jose import jwt

from authena_python_sdk.client import Client
from authena_python_sdk.models.user import User


def test_FUNC_client_user_refresh_token_WITH_valid_refresh_token_EXPECT_token_returned(
        sdk_client: Client,
        user: User
) -> None:
    """
    Test whether the refresh tokens action works as expected.

    :param sdk_client: SDK client fixture.
    :param user: User fixture.

    :return: No return.
    """

    def get_token_expiry(access_token: str) -> int:
        valid = sdk_client.user.validate_token(access_token)
        assert valid

        jwt_claims = jwt.get_unverified_claims(access_token)

        return jwt_claims['exp']

    tokens = sdk_client.user.create_token(user.username, user.password)
    token_expiry = get_token_expiry(tokens.access_token)

    # Do nothing for few seconds before refreshing the token.
    time.sleep(5)

    refreshed_tokens = sdk_client.user.refresh_token(tokens.refresh_token)
    refreshed_token_expiry = get_token_expiry(refreshed_tokens.access_token)

    assert refreshed_token_expiry > token_expiry
