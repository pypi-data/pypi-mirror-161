from dataclasses import dataclass
from typing import Optional, List


@dataclass
class User:
    username: str
    preferred_username: str
    email: str
    first_name: str
    last_name: str
    group_ids: Optional[List[str]] = None
    permissions: Optional[List[str]] = None
    tmp_password: Optional[str] = None
    password: Optional[str] = None
    is_active: bool = True
