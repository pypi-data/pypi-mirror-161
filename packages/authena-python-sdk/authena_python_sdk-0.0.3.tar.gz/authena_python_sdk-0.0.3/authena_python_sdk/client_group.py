from typing import Any, Dict, Optional, List

from authena_python_sdk.client_base import ClientBase
from authena_python_sdk.config import Config
from authena_python_sdk.models.group import Group


class ClientGroup(ClientBase):
    def __init__(
            self,
            api_key: str,
            api_secret: str,
            config: Optional[Config] = None
    ):
        super().__init__(api_key, api_secret, config)

    def get(self, group_id: str) -> Group:
        group_json = self.http_endpoint(
            path='/group/get',
            method='GET',
            fields={
                'group_id': group_id
            }
        ).call_to_json()

        return Group(
            group_id=group_json['group_id'],
            group_name=group_json['group_name'],
            permissions=group_json['permissions']
        )

    def delete(self, group_id: str) -> None:
        self.http_endpoint(
            path='/group/delete',
            method='DELETE',
            body={
                'group_id': group_id
            }
        ).call_to_response()

    def create(self, group_name: str, permissions: List[str], group_id: Optional[str] = None) -> Group:
        group_json = self.http_endpoint(
            path='/group/create',
            method='POST',
            body={
                'group_id': group_id,
                'group_name': group_name,
                'permissions': permissions
            }
        ).call_to_json()

        return Group(
            group_id=group_json['group_id'],
            group_name=group_json['group_name'],
            permissions=group_json['permissions']
        )

    def filter(self) -> Dict[str, Group]:
        groups_json: Dict[str, Any] = self.http_endpoint(
            path='/group/filter',
            method='GET'
        ).call_to_json()

        return {key: Group(
            group_id=group['group_id'],
            group_name=group['group_name'],
            permissions=group['permissions']
        ) for key, group in groups_json.items()}

    def update(self, group_id: str, group_name: Optional[str] = None, permissions: Optional[List[str]] = None) -> None:
        body = {
            'group_id': group_id,
            'group_name': group_name,
            'permissions': permissions
        }
        body = {key: value for key, value in body.items() if value is not None}

        self.http_endpoint(
            path='/group/update',
            method='PUT',
            body=body
        ).call_to_response()
