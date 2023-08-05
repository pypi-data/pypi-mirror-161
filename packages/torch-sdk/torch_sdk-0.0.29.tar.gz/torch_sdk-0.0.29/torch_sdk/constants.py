from enum import Enum, IntEnum, auto


class RuleExecutionStatus(Enum):
    STARTED = 1
    RUNNING = 2
    ERRORED = 3
    WARNING = 4
    SUCCESSFUL = 5
    ABORTED = 6


class FailureStrategy(IntEnum):
    DoNotFail = auto()
    FailOnError = auto()
    FailOnWarning = auto()


DATA_QUALITY = 'DATA_QUALITY'
RECONCILIATION = 'RECONCILIATION'
