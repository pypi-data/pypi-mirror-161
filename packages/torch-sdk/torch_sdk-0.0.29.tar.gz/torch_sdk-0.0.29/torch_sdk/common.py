from time import sleep
import logging
from torch_sdk.constants import RuleExecutionStatus, FailureStrategy, RECONCILIATION, DATA_QUALITY
from torch_sdk.models.ruleExecutionResult import RuleResult, RuleExecutionSummary
from torch_sdk.errors import APIError, TorchSdkException


LOGGER = logging.getLogger("common")


def get_callables(rule_type, torch_client):
    if rule_type == RECONCILIATION:
        result_call = torch_client.get_reconciliation_rule_result
        exec_call = torch_client.execute_reconciliation_rule
    elif rule_type == DATA_QUALITY:
        result_call = torch_client.get_dq_rule_result
        exec_call = torch_client.execute_dq_rule
    else:
        raise TorchSdkException(f'{rule_type} not found. Please provide correct rule_type.'
                                f' Allowed values are {RECONCILIATION}, {DATA_QUALITY}')
    return exec_call, result_call


class RuleExecutionResult:
    def __init__(self, execution_details):
        self.item = execution_details.items
        self.result = execution_details.result
        self.rule_id = execution_details.execution.ruleId
        self.rule_name = execution_details.execution.ruleName
        self.rule_version = execution_details.execution.ruleVersion
        self.rule_type = execution_details.execution.ruleType
        self.started_at = execution_details.execution.startedAt
        self.finished_at = execution_details.execution.finishedAt
        self.execution_id = execution_details.execution.id

    def __eq__(self, other):
        return self.execution_id == other.execution_id

    def __repr__(self):
        return f"RuleExecutionResult({self.__dict__})"


class Executor:
    def __init__(self, rule_type, torch_client, sync=False):
        self.id = None
        self.errorMessage = None
        self.sync = sync
        self.exec_call, self.result_call = get_callables(rule_type, torch_client)

    def is_id_valid(self):
        if self.id is None:
            execution_details = RuleResult()
            execution_details.execution = RuleExecutionSummary(
                executionStatus=RuleExecutionStatus.ERRORED, resultStatus=RuleExecutionStatus.ERRORED,
                executionError='valid execution_id is required.')
            LOGGER.info(execution_details.execution.executionError)
            return execution_details
        else:
            return True

    def get_status(self) -> RuleExecutionStatus:
        execution_id_check_passed = self.is_id_valid()
        if execution_id_check_passed is not True:
            return RuleExecutionStatus.ERRORED
        else:
            self.get_execution_status(self, self.id)

    def get_execution_status(self, execution_id) -> RuleExecutionStatus:
        LOGGER.info('Getting rule execution status.')
        try:
            execution_details = self.result_call(execution_id=execution_id)
            return_value = RuleExecutionStatus[execution_details.execution.resultStatus]
        except APIError as e:
            LOGGER.info(f'get_status failed due to http error. Details:{e}')
            return_value = RuleExecutionStatus.ERRORED
        except Exception as e:
            return_value = RuleExecutionStatus.ERRORED
            LOGGER.info(f'get_status failed due to Exception. Details:{e}')
            LOGGER.info(self.execution_details.execution.executionError)
        return return_value

    def get_result(self, sleep_interval=5, total_retries=0, failure_strategy: FailureStrategy = FailureStrategy.DoNotFail) -> RuleResult:
        execution_id_check_passed = self.is_id_valid()
        if execution_id_check_passed is not True:
            if failure_strategy >= FailureStrategy.FailOnError:
                raise TorchSdkException(execution_id_check_passed.execution.executionError)
            else:
                return execution_id_check_passed
        else:
            self.get_execution_result(self.id, sleep_interval, total_retries, failure_strategy)

    def get_execution_result(self, execution_id, sleep_interval=5, total_retries=0,
                             failure_strategy: FailureStrategy = FailureStrategy.DoNotFail) -> RuleResult:
        retry_count = 0
        try:
            while 1:
                execution_details = self.result_call(execution_id=execution_id)
                LOGGER.info(f'Checking rule execution result')
                if RuleExecutionStatus[execution_details.execution.executionStatus] == RuleExecutionStatus.RUNNING:
                    sleep(sleep_interval)
                    retry_count = retry_count + 1
                    if (total_retries == 0) or (total_retries > 0 and retry_count < total_retries):
                        continue
                    else:
                        execution_details.execution.executionError = f'Exiting after {total_retries} retries.'
                        LOGGER.info(execution_details.execution.executionError)
                        break
                else:
                    LOGGER.info('Rule completed.')
                    break
        except APIError as e:
            execution_details = RuleResult()
            execution_details.execution = RuleExecutionSummary(
                executionStatus=RuleExecutionStatus.ERRORED, resultStatus=RuleExecutionStatus.ERRORED,
                executionError=f'Rule execution failed due to http error. Details:{e}')
            LOGGER.info(execution_details.execution.executionError)
            if failure_strategy >= FailureStrategy.FailOnError:
                raise TorchSdkException(execution_details.execution.executionError)
        except Exception as e:
            execution_details = RuleResult()
            execution_details.execution = RuleExecutionSummary(
                executionStatus=RuleExecutionStatus.ERRORED, resultStatus=RuleExecutionStatus.ERRORED,
                executionError=f'Rule execution failed due to Exception. Details:{e}')
            LOGGER.info(execution_details.execution.executionError)
            if failure_strategy >= FailureStrategy.FailOnError:
                raise TorchSdkException(execution_details.execution.executionError)

        if RuleExecutionStatus[execution_details.execution.resultStatus] == RuleExecutionStatus.SUCCESSFUL:
            LOGGER.info('Rule completed successfully.')
        elif RuleExecutionStatus[execution_details.execution.resultStatus] == RuleExecutionStatus.WARNING:
            LOGGER.info('Rule completed with warnings.')
            if failure_strategy == FailureStrategy.FailOnWarning:
                raise TorchSdkException(f'Execution completed with warning. Details: {execution_details}')
        else:
            LOGGER.info(f'Rule execution completed with errors. Details:{execution_details}')
            if failure_strategy >= FailureStrategy.FailOnError:
                raise TorchSdkException(f'Rule execution completed with errors. Details: {execution_details}')
        return execution_details

    def execute(self, rule_id, incremental=False, sleep_interval=5, total_retries=0,
                failure_strategy: FailureStrategy = FailureStrategy.DoNotFail):
        try:
            execution_obj = self.exec_call(rule_id=rule_id, incremental=incremental)
            self.id = execution_obj.id
            if self.sync:
                self.get_execution_result(self.id, sleep_interval, total_retries, failure_strategy)
        except APIError as e:
            self.errorMessage = f'Rule execution failed due to http error. Details:{e}'
            LOGGER.info(self.errorMessage)
            if failure_strategy >= FailureStrategy.FailOnError:
                raise TorchSdkException(self.errorMessage)
        except Exception as e:
            self.errorMessage = f'Rule execution failed due to Exception. Details:{e}'
            LOGGER.info(self.errorMessage)
            if failure_strategy >= FailureStrategy.FailOnError:
                raise TorchSdkException(self.errorMessage)
