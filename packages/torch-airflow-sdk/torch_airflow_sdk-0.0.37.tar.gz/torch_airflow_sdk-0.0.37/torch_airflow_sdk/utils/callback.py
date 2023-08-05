from torch_sdk.models.pipeline import PipelineRunResult, PipelineRunStatus
from torch_airflow_sdk.utils.torch_client import TorchDAGClient
from datetime import datetime
from torch_sdk.events.generic_event import GenericEvent
from torch_airflow_sdk.utils.constants import get_dag_run_pipeline_run_id

# update pipeline with success status
def on_dag_failure_callback(context):
    """
    Used to update pipeline run with failure status of the corresponding span and end parent span as well. In case of failure it will send failure event as well.
    """
    task_instance = context['ti']
    pipeline_run_id = get_dag_run_pipeline_run_id(task_instance)
    print("pipeline_run_id in failure_callback", pipeline_run_id)
    client = TorchDAGClient()
    pipeline_run = client.get_pipeline_run(pipeline_run_id)
    parent_span = pipeline_run.get_root_span()
    parent_span.send_event(GenericEvent(context_data={'dag_status': 'FAILED', 'time': str(datetime.now())},
                                        event_uid=f'{parent_span.span.uid}.error.event'))
    parent_span.failed(context_data={'dag_status': 'FAILED', 'time': str(datetime.now())})
    pipeline_run.update_pipeline_run(
        context_data={'status': 'failure', 'dag': 'torch', 'context': str(context)},
        result=PipelineRunResult.FAILURE,
        status=PipelineRunStatus.FAILED
    )


# update pipeline with failed status
def on_dag_success_callback(context):
    """
    Used to update pipeline run with success status of the corresponding span and end span parent span
    """
    task_instance = context['ti']
    pipeline_run_id = get_dag_run_pipeline_run_id(task_instance)
    print("pipeline_run_id in success_callback", pipeline_run_id)
    client = TorchDAGClient()
    pipeline_run = client.get_pipeline_run(pipeline_run_id)
    parent_span = pipeline_run.get_root_span()
    parent_span.end(context_data={'dag_status': 'SUCCESS', 'time': str(datetime.now())})
    pipeline_run.update_pipeline_run(
        context_data={'status': 'success', 'dag': 'torch', 'context': str(context)},
        result=PipelineRunResult.SUCCESS,
        status=PipelineRunStatus.COMPLETED
    )