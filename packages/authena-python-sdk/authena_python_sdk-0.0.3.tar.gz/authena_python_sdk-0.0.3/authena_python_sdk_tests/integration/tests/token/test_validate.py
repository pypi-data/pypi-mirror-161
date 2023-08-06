from jose import jwt

from authena_python_sdk.client import Client
from authena_python_sdk.models.user import User


def test_FUNC_client_user_validate_token_WITH_valid_token_EXPECT_token_validity_confirmed(
        sdk_client: Client,
        user: User
) -> None:
    """
    Test whether the token validate works as expected.

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

    assert sdk_client.user.validate_token(access_token=tokens.access_token)
