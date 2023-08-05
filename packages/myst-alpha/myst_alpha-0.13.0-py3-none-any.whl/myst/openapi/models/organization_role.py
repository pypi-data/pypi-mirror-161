from enum import Enum


class OrganizationRole(str, Enum):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"

    def __str__(self) -> str:
        return str(self.value)
