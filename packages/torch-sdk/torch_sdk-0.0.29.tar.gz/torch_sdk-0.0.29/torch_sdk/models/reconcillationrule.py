from enum import Enum, auto
from torch_sdk.models.ruleExecutionResult import RuleExecutionResult, RuleItemResult, RuleExecutionSummary, RuleResult


class ReconRuleExecutionSummary(RuleExecutionSummary):
    def __init__(self, ruleId, executionMode, executionStatus, resultStatus, startedAt, executionType,
                 isProtectedResource, thresholdLevel, ruleVersion, id=None, ruleName=None, ruleType=None,
                 lastMarker=None, leftLastMarker=None, rightLastMarker=None, executionError=None, finishedAt=None,
                 resetPoint=None, persistencePath=None, resultPersistencePath=None, executorConfig=None,
                 markerConfig=None, leftMarkerConfig=None, rightMarkerConfig=None, **kwargs):
        super().__init__(ruleId, executionMode, executionStatus, resultStatus, startedAt,executionType, thresholdLevel,
                       ruleVersion, id, ruleName, ruleType, lastMarker, leftLastMarker, rightLastMarker, executionError,
                       finishedAt, resetPoint, persistencePath, resultPersistencePath, executorConfig, markerConfig,
                       leftMarkerConfig, rightMarkerConfig)
        self.isProtectedResource = isProtectedResource

    def __repr__(self):
        return f"ReconRuleExecutionSummary({self.__dict__})"


class ReconcillationRuleExecutionResult(RuleExecutionResult):
    def __init__(self, status, description=None, successCount=None, failureCount=None, leftRows=None, rightRows=None,
                 qualityScore=None, **kwargs):
        super().__init__(status, description, successCount, failureCount, qualityScore)
        self.leftRows = leftRows
        self.rightRows = rightRows

    def __repr__(self):
        return f"ReconcillationRuleExecutionResult({self.__dict__})"


class MappingOperation(Enum):
    EQ = auto()
    NOT_EQ = auto()
    GTE = auto()
    GT = auto()
    LTE = auto()
    LT = auto()


class Label:
    def __init__(self, key, value, **kwargs):
        self.key = key
        self.value = value

    def __repr__(self):
        return f"Label({self.__dict__})"


class ColumnMapping:
    def __init__(self, leftColumnName, operation, rightColumnName, useForJoining, isJoinColumnUsedForMeasure,
                 ignoreNullValues, weightage, ruleVersion,isWarning, businessExplanation=None, id=None,
                 reconciliationRuleId=None, deletedAt=None, labels=None, **kwargs):
        self.id = id
        self.leftColumnName = leftColumnName
        if isinstance(operation, dict):
            self.operation = MappingOperation(**operation)
        else:
            self.operation = operation
        self.rightColumnName = rightColumnName
        self.useForJoining = useForJoining
        self.isJoinColumnUsedForMeasure = isJoinColumnUsedForMeasure
        self.ignoreNullValues = ignoreNullValues
        self.weightage = weightage
        self.ruleVersion = ruleVersion
        self.isWarning = isWarning
        self.businessExplanation = businessExplanation
        self.reconciliationRuleId = reconciliationRuleId
        self.deletedAt = deletedAt
        self.labels = list()
        for obj in labels:
            if isinstance(obj, dict):
                self.labels.append(Label(**obj))
            else:
                self.labels.append(obj)

    def __repr__(self):
        return f"ColumnMapping({self.__dict__})"


class ReconcillationRuleItemResult(RuleItemResult):
    def __init__(self, id, ruleItemId, threshold, weightage, isRowMatchMeasure, isWarning, columnMapping=None,
                 resultPercent=None, success=None, error=None, **kwargs):
        super().__init__(id, ruleItemId, threshold, weightage, isWarning, resultPercent, success, error)
        self.isRowMatchMeasure = isRowMatchMeasure
        if isinstance(columnMapping, dict):
            self.columnMapping = ColumnMapping(**columnMapping)
        else:
            self.columnMapping = columnMapping

    def __repr__(self):
        return f"ReconcillationRuleItemResult({self.__dict__})"


class ReconcillationExecutionResult(RuleResult):
    def __init__(self, execution, items, meta=None, result=None, **kwargs):
        if isinstance(execution, dict):
            self.execution = ReconRuleExecutionSummary(**execution)
        else:
            self.execution = execution
        if isinstance(result, dict):
            self.result = ReconcillationRuleExecutionResult(**result)
        else:
            self.result = result
        self.items = list()
        for obj in items:
            if isinstance(obj, dict):
                self.items.append(ReconcillationRuleItemResult(**obj))
            else:
                self.items.append(obj)
        self.meta = meta
        self.executionId = self.execution.id

    def __repr__(self):
        return f"ReconcillationExecutionResult({self.__dict__})"
