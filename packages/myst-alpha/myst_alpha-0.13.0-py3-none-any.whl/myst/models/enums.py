import enum


@enum.unique
class DeployStatus(str, enum.Enum):
    NEW = "NEW"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

    def __str__(self) -> str:
        return str(self.value)


@enum.unique
class OrgSharingRole(str, enum.Enum):
    EDITOR = "EDITOR"
    VIEWER = "VIEWER"

    def __str__(self) -> str:
        return str(self.value)
