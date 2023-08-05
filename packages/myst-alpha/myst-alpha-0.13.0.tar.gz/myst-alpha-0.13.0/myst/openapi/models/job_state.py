from enum import Enum


class JobState(str, Enum):
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    UPSTREAM_FAILURE = "UPSTREAM_FAILURE"

    def __str__(self) -> str:
        return str(self.value)
