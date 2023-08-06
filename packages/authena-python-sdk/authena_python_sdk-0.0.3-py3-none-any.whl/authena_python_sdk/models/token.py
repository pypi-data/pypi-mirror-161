from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Token:
    token_type: str
    id_token: str
    expires_in: int
    access_token: str
    refresh_token: Optional[str] = None
