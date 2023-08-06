import json
import logging
import re
from urllib.parse import urlencode

import json_log_formatter
from boltons.iterutils import remap
from ddtrace import tracer
from flask import request

SENSITIVE_KEYS = re.compile(r'password|token|secret|key', flags=re.I)
MAX_BODY_SIZE = 50000
LOG_LEVEL_MAPPING = {
    'CRITICAL': 50,
    'ERROR': 40,
    'WARNING': 30,
    'INFO': 20,
    'DEBUG': 10,
}


def add_request_params_to_trace():
    """
    Add additional details about the current request (query string, body, request size) to
    the current Datadog trace. Useful for error handlers.
    """
    span = tracer.current_root_span()
    if not span:
        return

    # Log query string (if present) for all request methods
    query_params = request.args
    if query_params:
        clean = remap(query_params.copy(), visit=scrub_keys)
        span.set_tag('http.query_string', urlencode(clean))

    # Skip body logging if not POST, PATCH or PUT
    if request.method not in ['POST', 'PATCH', 'PUT']:
        return

    # Skip body logging if it's empty
    if not request.content_length:
        return

    span.set_tag('http.content_length', str(request.content_length))

    if request.content_length > MAX_BODY_SIZE:
        span.set_tag('http.body', 'Body too large, content could not be logged.')
        return

    # Try to parse body as JSON, and scrub sensitive values
    body = request.get_json(silent=True)
    if body:
        clean = remap(body, visit=scrub_keys)
        span.set_tag('http.body', json.dumps(clean))
    else:
        # If we can't parse as JSON, log the raw body
        body = request.get_data(as_text=True)
        span.set_tag('http.body', body)


def scrub_keys(path, key, value):
    if isinstance(key, str) and SENSITIVE_KEYS.search(key):
        return key, '-' * 5
    return key, value


def structure_logger(logger):
    def patch_level_func(level_func, level):
        def _patch_level_func(*args, **kwargs):
            extra = {**kwargs.get('extra', {}), **{'level': level}}
            return level_func(*args, **{**kwargs, **{'extra': extra}})

        return _patch_level_func

    def patch_log_func(log_func):
        reversed_mapping = dict([reversed(i) for i in LOG_LEVEL_MAPPING.items()])

        def _patch_log_func(level, *args, **kwargs):
            extra = {
                **kwargs.get('extra', {}),
                **{'level': reversed_mapping.get(level)},
            }
            return log_func(level, *args, **{**kwargs, **{'extra': extra}})

        return _patch_log_func

    # Insert level into json log for each level function invocation
    # ex. logger.info, logger.warning
    for level in LOG_LEVEL_MAPPING.keys():
        func = getattr(logger, level.lower())
        setattr(logger, level.lower(), patch_level_func(func, level))

    # Insert level into json log for direct log function call
    # ex logger.log
    func = getattr(logger, 'log')
    setattr(logger, 'log', patch_log_func(func))

    # Assign JSON formatter to handler
    json_handler = logging.StreamHandler()
    json_handler.setFormatter(json_log_formatter.JSONFormatter())
    logger.handlers = [json_handler]
    logger.propagate = False


def patch_celery_get_logger():
    # This has the opportunity of being a patch closer to the source (kombu)
    # Imports safely hidden behind structured_logging flag for now
    try:
        from celery.utils import log

        def _patch_func(name):
            l = log._get_logger(name)  # noqa: E741
            if logging.root not in (l, l.parent) and l is not log.base_logger:
                l = log._using_logger_parent(log.base_logger, l)  # noqa: E741
            structure_logger(l)
            return l

        log.get_logger = _patch_func
    except ModuleNotFoundError:
        return
