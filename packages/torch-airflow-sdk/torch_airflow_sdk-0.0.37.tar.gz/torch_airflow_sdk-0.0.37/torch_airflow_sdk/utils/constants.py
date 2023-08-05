from torch_airflow_sdk.utils.torch_client import TorchDAGClient
from torch_sdk.models.job import CreateJob, JobMetadata
from datetime import datetime

import logging

LOGGER = logging.getLogger("airflow.task")
PIPELINE_UID_XCOM = 'pipeline_uid_ff069534-5069-45b1-b737-aea6229db4bf'


def get_dag_run_pipeline_run_id(task_instance):
    return task_instance.xcom_pull(key=f'{task_instance.dag_id}_pipeline_run_id')


def create_job_span(task_instance, job_uid, inputs, outputs, metadata, context_job, bounded_by_span,
                    xcom_to_event_mapper_ids, span_uid, kwargs):
    try:
        xcom_context_data = {}
        span_uid_temp = span_uid
        pipeline_uid_ = task_instance.xcom_pull(key=PIPELINE_UID_XCOM)
        client = TorchDAGClient()
        pipeline = client.get_pipeline(pipeline_uid_)
        pipeline_run_id = get_dag_run_pipeline_run_id(task_instance)
        pipeline_run = pipeline.get_pipeline_run(pipeline_run_id)
        LOGGER.info("Creating job")
        job = CreateJob(
            uid=job_uid,
            name=f'{job_uid} Job',
            version=pipeline_run.versionId,
            description=f'{job_uid} created using torch job decorator',
            inputs=inputs,
            outputs=outputs,
            meta=metadata,
            context=context_job
        )
        job = pipeline.create_job(job)

    except Exception as e:
        LOGGER.error("Error in creating job")
        exception = e.__dict__
        LOGGER.error(exception)
        raise e
    else:
        LOGGER.info("Successfully created job.")
        if bounded_by_span:
            LOGGER.info('Sending Span Start event')
            try:
                xcoms = xcom_to_event_mapper_ids
                parent_span_context = task_instance.xcom_pull(key='parent_span_context')
                if parent_span_context is None:
                    LOGGER.debug('Sending new request to catalog to get parent span context')
                    parent_span_context = client.get_root_span(pipeline_uid=pipeline_uid_)
                else:
                    LOGGER.debug('Using xcom to get parent span context to send span event')
                associated_job_uids = [job_uid]
                if span_uid is None:
                    span_uid_temp = job_uid
                span_context = parent_span_context.create_child_span(
                    uid=span_uid_temp,
                    context_data={
                        'time': str(datetime.now()),
                        'xcom_to_event_mapper_ids': xcoms
                    },
                    associatedJobUids=associated_job_uids)
                if xcoms is None:
                    xcoms = []
                else:
                    for key in xcoms:
                        value = task_instance.xcom_pull(key=key)
                        if value is not None:
                            xcom_context_data[key] = value
                    LOGGER.info('Xcom context data ', xcom_context_data)
                kwargs['span_context_parent'] = span_context

            except Exception as ex:
                print(f'Span creation failed with exception{str(ex)}')
    return span_uid_temp, kwargs, xcom_context_data


def is_pipeline_run_ended(pipeline_run):
    if pipeline_run.status == "COMPLETED" or pipeline_run.status == "FAILED" or pipeline_run.status == "ABORTED":
        return True
