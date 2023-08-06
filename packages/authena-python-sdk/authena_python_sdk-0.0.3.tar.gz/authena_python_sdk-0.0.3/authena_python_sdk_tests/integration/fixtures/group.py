import uuid
from typing import Callable, List, Optional

from pytest import fixture

from authena_python_sdk.models.group import Group
from authena_python_sdk.client import Client
from b_lambda_layer_common.exceptions.container.not_found_error import NotFoundError


@fixture(scope='function')
def group_function(sdk_client: Client) -> Callable[..., Group]:
    """
    Fixture that returns a function.
    The function creates a group in the Authena and returns group object.

    This fixture does automatic cleanup (deletes created groups in the Authena) after test run.

    :return: Returns a function that creates a group object in the Authena and returns group object.
    """
    group_ids = []

    def __create_group(permissions: Optional[List[str]] = None) -> Group:
        group = sdk_client.group.create(
            group_name=str(uuid.uuid4()),
            permissions=permissions or []
        )

        group_ids.append(group.group_id)

        return group

    yield __create_group

    for group_id in group_ids:
        try:
            sdk_client.group.delete(group_id)
        except NotFoundError:
            # Group was not found, maybe deleted already, hence ignore this error.
            continue


@fixture(scope='function')
def group(group_function) -> Group:
    """
    Fixture that creates a group in the Authena
    and returns newly created group object.

    This fixture does automatic cleanup (deletes created groups in the Authena) after test run.

    :return: Returns a newly created and saved group.
    """

    return group_function()
