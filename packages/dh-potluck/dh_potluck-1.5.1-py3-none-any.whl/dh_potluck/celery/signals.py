from ddtrace import tracer

try:
    from celery.signals import task_prerun

    @task_prerun.connect
    def celer_task_prerun(task_id, task, args, **kwargs):
        # This will add the args specified in the celery task "dd_args" argument and add
        # them as tags to the current trace.

        # get the current span
        current_span = tracer.current_span()
        # set the host just once on the current span
        if current_span:
            if hasattr(task, 'dd_args'):
                for arg in task.dd_args:
                    if arg in task.request.kwargs:
                        current_span.set_tag(f'celery.task_args.{arg}', task.request.kwargs[arg])

except ModuleNotFoundError:
    pass
