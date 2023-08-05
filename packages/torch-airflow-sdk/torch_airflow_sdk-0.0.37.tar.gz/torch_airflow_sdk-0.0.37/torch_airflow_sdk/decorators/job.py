import functools
import logging
from datetime import datetime
from torch_sdk.events.generic_event import GenericEvent
from torch_airflow_sdk.utils.constants import create_job_span

LOGGER = logging.getLogger("airflow.task")


def job(job_uid=None, span_uid=None, inputs=[], outputs=[], metadata=None, xcom_to_event_mapper_ids=None, bounded_by_span=True):
    """
    Description:
    Use this decorator to create functional node (job) in your pipeline and crate span for your function inside your
     pipeline.
    :param job_uid: optional job uid of the pipeline. If not provided default job_id will bre created using dagname,
            task_id  and function name of function being wrapped
    :param span_uid: optional uid of the span. If not passed job_uid will get used as span_uid
    :param inputs: input arrays of the task
    :param outputs: output array of the job
    :param metadata: metadata of the job
    :param xcom_to_event_mapper_ids: xcom pull ids that you want to send with span event
    param bounded_by_span: optional True by default. Set True if you want span to be created for the job as well


    Example:
    @job(job_uid='customer.order.join.job',
        inputs=[Node('POSTGRES_LOCAL_DS.pipeline.pipeline.orders'), Node('POSTGRES_LOCAL_DS.pipeline.pipeline.customers')] ,
        outputs=[Node('POSTGRES_LOCAL_DS.pipeline.pipeline.customer_orders')],
        metadata=JobMetadata('name', 'team', 'code_location'),
        span_uid='customer.orders.datagen.span',
        bounded_by_span=True)
    def function(**context)

    """

    def decorator_job(func):
        @functools.wraps(func)
        def wrapper_job(*args, **kwargs):
            global xcom_context_data
            LOGGER.info(f"Job inputs:{inputs}")
            LOGGER.info(f"Job outputs:{outputs}")
            span_context = None
            task_instance = kwargs['ti']
            temp_job_uid = job_uid
            if temp_job_uid is None:
                temp_job_uid = f'{kwargs["dag"].dag_id}_{task_instance.task_id}_{func.__name__}'
            context_job = {'job': 'torch_job_decorator', 'time': str(datetime.now()), 'uid': temp_job_uid,
                           'function': str(func)}
            span_uid_temp, kwargs, xcom_context_data = create_job_span(
                task_instance=task_instance,
                job_uid=temp_job_uid,
                inputs=inputs,
                outputs=outputs,
                metadata=metadata,
                context_job=context_job,
                bounded_by_span=bounded_by_span,
                xcom_to_event_mapper_ids=xcom_to_event_mapper_ids,
                span_uid=span_uid,
                kwargs=kwargs
            )
            span_context = kwargs.get('span_context_parent', None)
            try:
                func(*args, **kwargs)
            except Exception as e:
                LOGGER.error("Sending Span End Event with status Failure")
                exception = e.__dict__
                LOGGER.error(exception)
                if span_context is not None:
                    span_context.send_event(
                        GenericEvent(context_data={'status': 'error', 'error_data': str(e), 'time': str(datetime.now()),
                                                   'exception_type': str(type(e).__name__)},
                                     event_uid=f'{span_uid_temp}.error.event'))
                    span_context.failed(context_data=xcom_context_data)
                raise e
            else:
                LOGGER.info("Sending Span End event with status Success")
                if span_context is not None:
                    span_context.end(context_data=xcom_context_data)

        return wrapper_job

    return decorator_job
