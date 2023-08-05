from torch_sdk.models.ruleExecutionResult import RuleExecutionResult, RuleItemResult, RuleResult, RuleExecutionSummary


class RootCauseAnalysis:
    def __init__(self, key, bad, good, badFraction, goodFraction, **kwargs):
        self.key = key
        self.bad = bad
        self.good = good
        self.badFraction = badFraction
        self.goodFraction = goodFraction

    def __repr__(self):
        return f"RootCauseAnalysis({self.__dict__})"


class DataQualityRuleExecutionResult(RuleExecutionResult):
    def __init__(self, status, description=None, successCount=None, failureCount=None, rows=None, failedRows=None,
                 qualityScore=None, rca=None, **kwargs):
        super().__init__(status, description, successCount, failureCount, qualityScore)
        self.failedRows = failedRows
        self.rows = rows
        if isinstance(rca, dict):
            self.rca = RootCauseAnalysis(**rca)
        else:
            self.rca = rca
    
    def __repr__(self):
        return f"DataQualityRuleExecutionResult({self.__dict__})"


class DataQualityRuleItemResult(RuleItemResult):
    def __init__(self, id, ruleItemId, threshold, weightage, isWarning, resultPercent=None, businessItemId=None,
                 success=None, error=None, **kwargs):
        super().__init__(id, ruleItemId, threshold, weightage, isWarning, resultPercent, success, error)
        self.businessItemId = businessItemId

    def __repr__(self):
        return f"DataQualityRuleItemResult({self.__dict__})"


class DataQualityExecutionResult(RuleResult):
    def __init__(self, execution, items, meta=None, result=None, **kwargs):
        if isinstance(execution, dict):
            self.execution = RuleExecutionSummary(**execution)
        else:
            self.execution = execution
        if isinstance(result, dict):
            self.result = DataQualityRuleExecutionResult(**result)
        else:
            self.result = result
        self.items = list()
        for obj in items:
            if isinstance(obj, dict):
                self.items.append(DataQualityRuleItemResult(**obj))
            else:
                self.items.append(obj)
        self.meta = meta
        self.executionId = self.execution.id

    def __repr__(self):
        return f"DataQualityExecutionResult({self.__dict__})"
