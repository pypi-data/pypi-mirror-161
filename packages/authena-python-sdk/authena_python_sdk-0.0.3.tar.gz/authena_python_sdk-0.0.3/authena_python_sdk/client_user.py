from typing import Optional, List, Dict

from authena_python_sdk.client_base import ClientBase
from authena_python_sdk.config import Config
from authena_python_sdk.models.token import Token
from authena_python_sdk.models.user import User


class ClientUser(ClientBase):
    def __init__(
            self,
            api_key: str,
            api_secret: str,
            config: Optional[Config] = None
    ):
        super().__init__(api_key, api_secret, config)

    def get(self, username: str) -> User:
        user_json = self.http_endpoint(
            path='/user/get',
            method='GET',
            fields={
                'username': username
            }
        ).call_to_json()

        return User(
            group_ids=user_json['group_ids'],
            username=user_json['username'],
            preferred_username=user_json['preferred_username'],
            email=user_json['email'],
            first_name=user_json['first_name'],
            last_name=user_json['last_name'],
            permissions=user_json['permissions'],
            is_active=user_json['is_active']
        )

    def delete(self, username: str) -> None:
        self.http_endpoint(
            path='/user/delete',
            method='DELETE',
            body={
                'username': username,
            }
        ).call_to_response()

    def create(
            self,
            email: str,
            preferred_username: str,
            first_name: str,
            last_name: str,
            username: Optional[str] = None,
            group_ids: Optional[List[str]] = None,
            permissions: Optional[List[str]] = None
    ) -> User:
        user_json = self.http_endpoint(
            path='/user/create',
            method='POST',
            body={
                'username': username,
                'group_ids': group_ids,
                'email': email,
                'preferred_username': preferred_username,
                'first_name': first_name,
                'last_name': last_name,
                'permissions': permissions
            }
        ).call_to_json()

        return User(
            group_ids=group_ids,
            username=user_json['username'],
            preferred_username=preferred_username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            tmp_password=user_json['tmp_password'],
            permissions=permissions
        )

    def enable(self, username: str) -> None:
        self.http_endpoint(
            path='/user/enable',
            method='POST',
            body={
                'username': username
            }
        ).call_to_response()

    def disable(self, username: str) -> None:
        self.http_endpoint(
            path='/user/disable',
            method='POST',
            body={
                'username': username
            }
        ).call_to_response()

    def update(
            self,
            username: str,
            email: Optional[str] = None,
            preferred_username: Optional[str] = None,
            first_name: Optional[str] = None,
            last_name: Optional[str] = None,
            group_ids: Optional[List[str]] = None,
            permissions: Optional[List[str]] = None
    ) -> None:
        body = {
            'username': username,
            'email': email,
            'preferred_username': preferred_username,
            'first_name': first_name,
            'last_name': last_name,
            'group_ids': group_ids,
            'permissions': permissions
        }
        body = {key: value for key, value in body.items() if value is not None}

        self.http_endpoint(
            path='/user/update',
            method='PUT',
            body=body
        ).call_to_response()

    def filter(
            self,
            group_id: Optional[str] = None,
            usernames: Optional[List[str]] = None,
            is_active: Optional[bool] = None
    ) -> Dict[str, User]:
        response_body_json = self.http_endpoint(
            path='/user/filter',
            method='GET',
            fields=[
                ('group_id', group_id),
                ('is_active', is_active),
                *[('username', username) for username in usernames or []]
            ]
        ).call_to_json()

        users = {}
        for username, user_dict in response_body_json.items():
            users[username] = User(
                group_ids=user_dict['group_ids'],
                username=user_dict['username'],
                preferred_username=user_dict['preferred_username'],
                email=user_dict['email'],
                first_name=user_dict['first_name'],
                last_name=user_dict['last_name'],
            )

        return users

    def confirm(self, username: str, tmp_password: str, new_password: str) -> None:
        token_json = self.http_endpoint(
            path='/token/create',
            method='POST',
            body={
                'username': username,
                'password': tmp_password
            }
        ).call_to_json()

        if token_json['is_challenge'] is True:
            token_json = self.http_endpoint(
                path='/token/challenge',
                method='POST',
                body={
                    'challenge_name': token_json['challenge']['challenge_name'],
                    'challenge_session': token_json['challenge']['session'],
                    'challenge_response': {
                        'USERNAME': username,
                        'NEW_PASSWORD': new_password
                    }
                }
            ).call_to_json()

        try:
            access_token = token_json['authentication']['access_token']
        except (KeyError, ValueError):
            access_token = None

        if not access_token:
            raise ValueError(
                'Something went wrong. '
                'Access token was not created, hence, the new user probably was not confirmed. '
                'Please try again, or contact administrators.'
            )

    def validate_token(self, access_token: str) -> bool:
        response = self.http_endpoint(
            path='/token/validate',
            method='POST',
            body={
                'access_token': access_token
            }
        ).call_to_json()

        return response['valid']

    def create_token(self, username: str, password: str) -> Token:
        token_json = self.http_endpoint(
            path='/token/create',
            method='POST',
            body={
                'username': username,
                'password': password
            }
        ).call_to_json()

        if token_json['is_challenge'] is True:
            raise ValueError(
                f'User was not confirmed. '
                f'Please confirm user first, before creating tokens. '
                f'Hint: to confirm user, call "{ClientUser.__name__}.{ClientUser.confirm.__name__}" method.'
            )

        return Token(**token_json['authentication'])

    def exchange_auth_code(self, authorization_code: str, redirect_uri: Optional[str] = None) -> Token:
        token_json = self.http_endpoint(
            path='/token/create',
            method='POST',
            body={
                'authorization_code': authorization_code,
                'redirect_uri': redirect_uri
            }
        ).call_to_json()

        return Token(**token_json['authentication'])

    def refresh_token(self, refresh_token: str) -> Token:
        token_json = self.http_endpoint(
            path='/token/refresh',
            method='POST',
            body={
                'refresh_token': refresh_token
            }
        ).call_to_json()

        return Token(**token_json)

    def permissions(self, username: str) -> List[str]:
        permissions = self.http_endpoint(
            path='/permission/get',
            method='GET',
            fields={
                'username': username
            }
        ).call_to_json()

        return permissions['permissions']
