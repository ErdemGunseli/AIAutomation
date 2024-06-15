from enum import Enum


class MessageType(Enum):
    USER = "user"
    SYSTEM = "system"
    ASSISTANT = "assistant"


class AutomationResult(Enum):
    # Conditions were met and the automation action was executed:
    EXECUTED = "executed"
    # Some/all conditions were not met and the automation action was not executed:
    NOT_EXECUTED = "not_executed"
    # Some error occurred - either when checking the conditions or running the action:
    FAILED = "failed"