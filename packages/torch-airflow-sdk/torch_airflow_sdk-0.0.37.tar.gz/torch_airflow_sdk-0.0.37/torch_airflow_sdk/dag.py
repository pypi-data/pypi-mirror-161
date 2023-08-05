from airflow import DAG
from airflow.utils.log.logging_mixin import LoggingMixin
from torch_airflow_sdk.decorators.handle_callback import handle_dag_callback
from torch_airflow_sdk.utils.callback import on_dag_success_callback, on_dag_failure_callback


class DAG(DAG, LoggingMixin):
    """
    Description:
        DAG Wrapper created by torch. To observe airflow ETL in torch UI.
    A dag (directed acyclic graph) is a collection of tasks with directional
    dependencies. A dag also has a schedule, a start date and an end date
    (optional). For each schedule, (say daily or hourly), the DAG needs to run
    each individual tasks as their dependencies are met. Certain tasks have
    the property of depending on their own past, meaning that they can't run
    until their previous schedule (and upstream tasks) are completed.

    DAGs essentially act as namespaces for tasks. A task_id can only be
    added once to a DAG.

    To create DAG, you can optionally pass 2 additional parameters override_success_callback, override_failure_callback.
    Other parameters will be same as standard apache airflow DAG.
    :param override_success_callback: (True) If we do not want the pipeline run to be ended at the end of the
     successful run of the DAG
    :param override_failure_callback: (True) If we do not want the pipeline run to be ended at the end of the
    unsuccessful run of the DAG

    """
    def __init__(self, *args, **kwargs):
        """
            Description:
            To create DAG, you can optionally pass 2 additional parameters override_success_callback, override_failure_callback.
            Other parameters will be same as standard apache airflow DAG.
        :param override_success_callback: (True) optional If we do not want the pipeline run to be ended at the end of
         the successful run of the DAG
        :param override_failure_callback: (True) optional If we do not want the pipeline run to be ended at the end of
        the unsuccessful run of the DAG
        """

        success_callback_func = kwargs.pop('on_success_callback', None)
        is_override_success_callback = kwargs.pop('override_success_callback', False)

        if success_callback_func is not None and not is_override_success_callback:
            success_callback_func = handle_dag_callback(success_callback_func)
        elif not is_override_success_callback:
            success_callback_func = on_dag_success_callback

        failure_callback_func = kwargs.pop('on_failure_callback', None)
        is_override_failure_callback = kwargs.pop('override_failure_callback', False)

        if failure_callback_func is not None and not is_override_failure_callback:
            failure_callback_func = handle_dag_callback(failure_callback_func)
        elif not is_override_failure_callback:
            failure_callback_func = on_dag_failure_callback

        super(DAG, self).__init__(
            on_failure_callback=failure_callback_func,
            on_success_callback=success_callback_func,
            *args, **kwargs)
