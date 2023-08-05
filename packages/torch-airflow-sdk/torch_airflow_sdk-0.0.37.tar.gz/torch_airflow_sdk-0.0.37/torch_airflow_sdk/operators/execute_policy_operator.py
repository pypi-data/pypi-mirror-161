from airflow.models.baseoperator import BaseOperator
from torch_sdk.torch_client import TorchClient
from torch_airflow_sdk.initialiser import torch_credentials
from torch_sdk.constants import FailureStrategy
import logging
LOGGER = logging.getLogger("tasks")


class ExecutePolicyOperator(BaseOperator):
    """
    Description:
        ExecutePolicyOperator is used to execute a policy by passing rule_type and rule_id.
        It will return only after the execution ends if sync is set to True.

        :param rule_type: (String) TYpe of rule to be executed
        :param rule_id: (String) id of the rule to be executed
        :param incremental: (bool) optional Set it to True if full execution has to be done
        :param sync: (bool) optional Set it to True to execute policy in synchronous mode
        :param failure_strategy: (enum) optional Set it to decide if it should fail at error,
            fail at warning or never fail
    """

    def __init__(self, *, rule_type, rule_id, sync, incremental=False,
                 failure_strategy: FailureStrategy = FailureStrategy.DoNotFail, **kwargs):
        """
        :param rule_type: (String) TYpe of rule to be executed
        :param rule_id: (String) id of the rule to be executed
        :param incremental: (bool) optional Set it to True if full execution has to be done
        :param sync: (bool) optional Set it to True to execute policy in synchronous mode
        :param failure_strategy: (enum) optional Set it to decide if it should fail at error,
            fail at warning or never fail

        Example:
        from torch_sdk.constants import RuleExecutionStatus, FailureStrategy, RECONCILIATION, DATA_QUALITY
        from torch_sdk.common import Executor
        operator_task = ExecutePolicyOperator(
            task_id='torch_pipeline_operator_test',
            rule_type=DATA_QUALITY,
            rule_id=46,
            sync=True,
            failure_strategy=FailureStrategy.FailOnError,
            dag=dag
        )

        In case you need to query the status in another task you need to pull the execution id from xcom by passing
        the rule name in the {rule_name}_execution_id. In this example the rule name of rule _id 46 is 'policy_with_email'

        After getting the execution_id you need to create object of Executor by passing rule_type and
        torch_client object and call get_result using the execution_id.

        def operator_result(**context):
            xcom_key = {rule_type}_{rule_id}_execution_id'
            task_instance = context['ti']
            # get the rule_name and execution id - then pull from xcom
            execution_id = task_instance.xcom_pull(key=xcom_key)
            if execution_id is not None:
                torch_client = TorchClient(**torch_credentials)
                result = torch_client.get_rule_result(rule_type=const.DATA_QUALITY, execution_id=execution_id)
        """
        super().__init__(**kwargs)
        self.rule_type = rule_type
        self.rule_id = rule_id
        self.incremental = incremental
        self.failure_strategy = failure_strategy
        self.sync = sync

    def execute(self, context):
        torch_client = TorchClient(**torch_credentials)
        execution_return = torch_client.execute_rule(
            rule_type=self.rule_type,
            rule_id=self.rule_id,
            sync=self.sync,
            incremental=self.incremental,
            failure_strategy=self.failure_strategy)
        if execution_return.id is not None:
            xcom_key = f'{self.rule_type}_{self.rule_id}_execution_id'
            task_instance = context['ti']
            # get the rule_name and execution id - then push them in xcom
            task_instance.xcom_push(key=xcom_key, value=execution_return.id)

