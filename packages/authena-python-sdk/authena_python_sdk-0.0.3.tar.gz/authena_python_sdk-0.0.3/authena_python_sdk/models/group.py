from typing import Optional, List
from dataclasses import dataclass, field


@dataclass
class Group:
    group_id: str
    group_name: str
    permissions: Optional[List[str]] = field(default_factory=lambda: [])
