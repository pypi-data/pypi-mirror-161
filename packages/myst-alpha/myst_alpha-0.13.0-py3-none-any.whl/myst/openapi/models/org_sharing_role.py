from enum import Enum


class OrgSharingRole(str, Enum):
    EDITOR = "EDITOR"
    VIEWER = "VIEWER"

    def __str__(self) -> str:
        return str(self.value)
