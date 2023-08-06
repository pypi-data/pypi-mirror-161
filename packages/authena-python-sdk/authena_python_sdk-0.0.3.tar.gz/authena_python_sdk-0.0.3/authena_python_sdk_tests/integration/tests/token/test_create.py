from unittest.mock import patch, MagicMock
from uuid import uuid4

from b_lambda_layer_common.util.http_endpoint import HttpEndpoint

from authena_python_sdk.client import Client
from authena_python_sdk.models.user import User


def test_FUNC_client_user_create_token_WITH_username_password_EXPECT_token_created(sdk_client: Client, user: User) -> None:
    """
    Check whether the tokens can be created when username and password of an existing user are given.

    :param sdk_client: Authena SDK client fixture.
    :param user: User fixture.

    :return: No return.
    """
    # Try to get a new authentication tokens.
    tokens = sdk_client.user.create_token(user.username, user.password)

    # Validate issued access token.
    valid = sdk_client.user.validate_token(tokens.access_token)

    # Assert token validity.
    assert valid


@patch.object(HttpEndpoint, 'call_to_json')
def test_FUNC_client_user_exchange_auth_code_WITH_authorization_code_EXPECT_token_created(
        http_endpoint_mock: MagicMock,
        sdk_client: Client,
        user: User
) -> None:
    """
    Check whether the tokens can be created when authorization code is given.

    :param sdk_client: Authena SDK client fixture.
    :param user: User fixture.

    :return: No return.
    """
    id_token = str(uuid4()).replace('-', '')
    access_token = str(uuid4()).replace('-', '')
    refresh_token = str(uuid4()).replace('-', '')
    http_endpoint_mock.return_value = {
        "authentication": {
            "id_token": id_token,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": 3600,
            "token_type": "Bearer"
        }
    }

    tokens = sdk_client.user.exchange_auth_code(authorization_code=str(uuid4()))

    assert tokens.id_token == id_token, tokens.id_token
    assert tokens.access_token == access_token, tokens.access_token
    assert tokens.refresh_token == refresh_token, tokens.refresh_token
