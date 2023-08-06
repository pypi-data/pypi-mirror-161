# Authena Python SDK

## Description

**Authena Python SDK** allows an easy and fast integration with **AUTHENA** - authentication and authorization API.

#### Remarks

[Biomapas](https://biomapas.com) aims to modernize life-science
industry by sharing its IT knowledge with other companies and
the community. This is an open source library intended to be used
by anyone. Improvements and pull requests are welcome.

#### Related technology

- Python 3

#### Assumptions

The project assumes the following:

- You have basic-good knowledge in python programming.

#### Install

The project is built and uploaded to PyPi. Install it by using pip.

```
pip install authena_python_sdk
```

Or directly install it through source.

```
pip install .
```

## Usage & Examples

### SDK client

Create **Authena SDK** client using the given **AUTHENA PUBLIC API URL**, **API KEY**, and **API SECRET**:

```python
from authena_python_sdk.client import Client
from authena_python_sdk.config import Config

AUTHENA_PUBLIC_API_URL = 'http://localhost'
AUTHENA_API_KEY = 'DFCC345BE3C0DC42DF8A123F7579'
AUTHENA_API_SECRET = '4AomCEeUG2j7epT87GahHfh2e8YnaDRthx5k0zfgnnY='

sdk_client = Client(
    api_key=AUTHENA_API_KEY,
    api_secret=AUTHENA_API_SECRET,
    config=Config(
        public_api_url=AUTHENA_PUBLIC_API_URL
    )
)
```

### Create a user

To create user, use SDK client method - user.create.

**Request syntax:**

```python
response = sdk_client.user.create(
    email='string',
    preferred_username='string',
    first_name='string',
    last_name='string',
    username='string',
    group_ids=['string', 'string', '...'],
    permissions=['string', 'string', '...']
)
```

**Parameters**

- **email** (string) [REQUIRED] - Email address of the user.
- **preferred_username** (string) [REQUIRED] - Preferred username of the user.
- **first_name** (string) [REQUIRED] - Given name of the user.
- **last_name** (string) [REQUIRED] - Family name of the user.
- **username** (string) [OPTIONAL] - Unique idnetifier of the user.
- **group_ids** (list) [OPTIONAL] - A list of group unique identifiers.
- **permissions** (list) [OPTIONAL] - A list of user permissions.

**Returns**

Return Type: User

**User Attributes**:

- **username** (string) - Unique identifier of newly created user.
- **preferred_username** (string) - Preferred username of newly created user.
- **email** (string) - Email address of newly created user.
- **first_name** (string) - Given name of newly created user.
- **last_name** (string) - Family name of newly created user.
- **tmp_password** (string) - Temporary password of newly created user.
- **group_ids** (list) - A list of unique identifiers of assigned permission groups.
- **permissions** (list) - A list of directly assigned user permissions.

### Get User

Retrieval of previously created user.

**Request syntax:**

```python
response = sdk_client.user.get(username='string')
```

**Parameters**

- **username** (string) [REQUE] - Unique idnetifier of the user.

**Returns**

Return Type: User

**User Attributes**:

- **username** (string) - Unique identifier of newly created user.
- **preferred_username** (string) - Preferred username of newly created user.
- **email** (string) - Email address of newly created user.
- **first_name** (string) - Given name of newly created user.
- **last_name** (string) - Family name of newly created user.
- **group_ids** (list) - A list of unique identifiers of assigned permission groups.
- **permissions** (list) - A list of directly assigned user permissions.
- **is_active** (bool) - Specifies whether the user is enabled.

Please check the documentation available here, which contains information on how to use the library, 
and a complete API reference guide.

#### Testing

The project has tests that can be run. Simply run:

```
pytest authena_python_sdk_tests
```

#### Contribution

Found a bug? Want to add or suggest a new feature?<br>
Contributions of any kind are gladly welcome. You may contact us
directly, create a pull-request or an issue in github platform.
Lets modernize the world together.
