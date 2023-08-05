from enum import Enum, auto


class RuleType(Enum):
    DATA_QUALITY = auto()
    RECONCILIATION = auto()
    EQUALITY = auto()
    DATA_DRIFT = auto()
    SCHEMA_DRIFT = auto()


class RuleExecutionMode(Enum):
    SCHEDULED = auto()
    MANUAL = auto()
    WEBHOOK = auto()
    API = auto()


class RuleExecutionStatus(Enum):
    STARTED = auto()
    RUNNING = auto()
    ERRORED = auto()
    WARNING = auto()
    SUCCESSFUL = auto()
    ABORTED = auto()


class RuleResultStatus(Enum):
    STARTED = auto()
    RUNNING = auto()
    ERRORED = auto()
    WARNING = auto()
    SUCCESSFUL = auto()
    ABORTED = auto()


class PolicyExecutionType(Enum):
    SAMPLE = auto()
    FULL = auto()
    INCREMENTAL = auto()


class RuleThresholdLevel:
    def __init__(self, success, warning=None, **kwargs):
        self.success = success
        self.warning = warning

    def __repr__(self):
        return f"RuleThresholdLevel({self.__dict__})"


class LivyExecutorConfig:
    def __init__(self, executorMemory=None, executorCores=None, numExecutors=None, **kwargs):
        self.executorMemory = executorMemory
        self.executorCores = executorCores
        self.numExecutors = numExecutors

    def __repr__(self):
        return f"LivyExecutorConfig({self.__dict__})"


class DataBricksExecutorConfig:
    def __init__(self, minWorkers=None, maxWorkers=None, clusterWorkerType=None, clusterDriverType=None, **kwargs):
        self.minWorkers = minWorkers
        self.maxWorkers = maxWorkers
        self.clusterWorkerType = clusterWorkerType
        self.clusterDriverType = clusterDriverType

    def __repr__(self):
        return f"DataBricksExecutorConfig({self.__dict__})"


class ExecutorConfig:
    def __init__(self, livy=None, databricks=None, **kwargs):
        if isinstance(livy, dict):
            self.livy = LivyExecutorConfig(**livy)
        else:
            self.livy = livy
        if isinstance(databricks, dict):
            self.databricks = DataBricksExecutorConfig(**databricks)
        else:
            self.databricks = databricks

    def __repr__(self):
        return f"ExecutorConfig({self.__dict__})"


class RuleExecutionSummary:
    def __init__(self, ruleId=None, executionMode=None, executionStatus=None, resultStatus=None, startedAt=None,
                 executionType=None, thresholdLevel=None, ruleVersion=None, id=None, ruleName=None, ruleType=None,
                 lastMarker=None, leftLastMarker=None, rightLastMarker=None, executionError=None, finishedAt=None,
                 resetPoint=None, persistencePath=None, resultPersistencePath=None, executorConfig=None,
                 markerConfig=None, leftMarkerConfig=None, rightMarkerConfig=None, **kwargs):

        self.ruleId = ruleId
        self.id = id
        self.ruleName = ruleName
        if isinstance(ruleType, dict):
            self.ruleType = RuleType(**ruleType)
        else:
            self.ruleType = ruleType
        if isinstance(executionMode, dict):
            self.executionMode = RuleExecutionMode(**executionMode)
        else:
            self.executionMode = executionMode
        if isinstance(executionStatus, dict):
            self.executionStatus = RuleExecutionStatus(**executionStatus)
        else:
            self.executionStatus = executionStatus
        if isinstance(resultStatus, dict):
            self.resultStatus = RuleResultStatus(**resultStatus)
        else:
            self.resultStatus = resultStatus

        self.lastMarker = lastMarker
        self.leftLastMarker = leftLastMarker
        self.rightLastMarker = rightLastMarker
        self.executionError = executionError
        self.startedAt = startedAt
        self.finishedAt = finishedAt

        if isinstance(thresholdLevel, dict):
            self.thresholdLevel = RuleThresholdLevel(**thresholdLevel)
        else:
            self.thresholdLevel = thresholdLevel
        self.resetPoint = resetPoint
        self.persistencePath = persistencePath
        self.resultPersistencePath = resultPersistencePath
        self.ruleVersion = ruleVersion
        if isinstance(executorConfig, dict):
            self.executorConfig = ExecutorConfig(**executorConfig)
        else:
            self.executorConfig = executorConfig
        self.markerConfig = markerConfig
        self.leftMarkerConfig = leftMarkerConfig
        self.rightMarkerConfig = rightMarkerConfig
        if isinstance(executionType, dict):
            self.executionType = PolicyExecutionType(**executionType)
        else:
            self.executionType = executionType

    def __repr__(self):
        return f"RuleExecutionSummary({self.__dict__})"


class RuleExecutionResult:
    def __init__(self, status, description=None, successCount=None, failureCount=None, qualityScore=None, **kwargs):
        if isinstance(status, dict):
            self.status = RuleResultStatus(**status)
        else:
            self.status = status
        self.description = description
        self.successCount = successCount
        self.failureCount = failureCount
        self.qualityScore = qualityScore


class RuleItemResult:
    def __init__(self, id, ruleItemId, threshold, weightage, isWarning, resultPercent=None, businessItemId=None,
                 success=None, error=None, **kwargs):
        self.id = id
        self.ruleItemId = ruleItemId
        self.businessItemId = businessItemId
        self.threshold = threshold
        self.resultPercent = resultPercent
        self.success = success
        self.error = error
        self.weightage = weightage
        self.isWarning = isWarning

    def __repr__(self):
        return f"RuleItemResult({self.__dict__})"


class RuleResult:
    def __init__(self, execution: RuleExecutionSummary = None, items: [RuleItemResult] = None, meta=None,
                 result: RuleExecutionResult = None, **kwargs):
        self.execution = execution
        self.items = items
        self.meta = meta
        self.result = result

    def __repr__(self):
        return f"RuleResult({self.__dict__})"
