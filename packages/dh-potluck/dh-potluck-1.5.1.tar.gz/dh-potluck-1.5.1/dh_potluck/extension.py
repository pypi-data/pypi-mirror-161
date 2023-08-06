import importlib
import logging
import os
import threading
import traceback
from http import HTTPStatus
from http.client import RemoteDisconnected

import pkg_resources
from ddtrace import tracer
from flask import Blueprint, g, jsonify, render_template, request
from flask_limiter import Limiter
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException, InternalServerError
from werkzeug.middleware.proxy_fix import ProxyFix

from .auth import get_user, role_required
from .logging import add_request_params_to_trace, patch_celery_get_logger, structure_logger
from .platform_connection import PlatformConnectionError
from .queries_summary import get_database_queries_summary


class DHPotluck:
    _app = None
    _app_token = None
    _structured_logging_enabled = False
    _rate_limiting_enabled = False
    _rate_limit = None
    _limiter = None
    _validate_token_func = None

    def __init__(self, app=None, **kwargs):
        """Initialize dh-potluck."""
        self._app = app

        if app is not None:
            self.init_app(app, **kwargs)

    def init_app(self, app, **kwargs):
        self._app = app
        self._app_token = app.config['DH_POTLUCK_APP_TOKEN']
        self._structured_logging_enabled = app.config.get('STRUCTURED_LOGGING')
        self._rate_limiting_enabled = bool(app.config.get('RATELIMIT_ENABLED', 0))
        self._rate_limit = app.config.get('RATELIMIT_DEFAULT_PER_MINUTE', 1000)

        # Import function we use to authenticate incoming requests
        validate_func_name = app.config.get(
            'DH_POTLUCK_VALIDATE_TOKEN_FUNC', 'dh_potluck.auth.validate_token_using_api'
        )
        module_name, class_name = validate_func_name.rsplit('.', 1)
        self._validate_token_func = getattr(importlib.import_module(module_name), class_name)

        # Adjust the WSGI environ based on X-Forwarded- headers that proxies in front of the
        # application may set.
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

        # Disable Datadog tracing when testing
        tracer.configure(enabled=not app.config.get('TESTING', False))
        tracer.set_tags(
            {'dh_potluck.version': pkg_resources.get_distribution('dh-potluck').version}
        )

        self._configure_api_docs()
        self._limiter = self._configure_rate_limiting()
        self._app.before_request(self._process_request)
        self._app.after_request(self._process_response)
        self._register_error_handlers()

        if app.config.get('STRUCTURED_LOGGING'):
            self._configure_structured_logging()

        # Datadog Profiling - ddtrace 0.39.0 required
        if app.config.get('DD_PROFILING'):
            import ddtrace.profiling.auto  # noqa: F401

    def _get_rate_limit_key(self):
        """
        Extract a key from the request we can identify users by so we can rate limit appropriately.
        """
        if 'Authorization' in request.headers:
            return request.headers['Authorization'].split(' ')[1]
        else:
            ip = request.remote_addr
            if request.headers.getlist('X-Forwarded-For'):
                ip = request.headers.getlist('X-Forwarded-For')[0]
            return ip

    def _configure_api_docs(self):
        """
        Render ReDoc for DH API docs.
        """
        api_docs = Blueprint(
            'API Docs', __name__, url_prefix='/docs', template_folder='./templates'
        )

        @api_docs.route('')
        def render_docs():
            return render_template('dhdocs.html')

        self._app.register_blueprint(api_docs)

    def _configure_rate_limiting(self):
        limiter = Limiter(
            key_func=self._get_rate_limit_key,
            default_limits=[f'{self._rate_limit} per minute'],
            default_limits_per_method=False,
            headers_enabled=True,
            swallow_errors=True,
            enabled=self._rate_limiting_enabled,
        )

        @limiter.request_filter
        def app_token_whitelist():
            return request.headers.get('Authorization', '') == f'Application {self._app_token}'

        limiter.init_app(self._app)
        return limiter

    def _configure_structured_logging(self):
        # Configure root logger
        structure_logger(logging.getLogger())

        # Set all others
        for logger in [logging.getLogger(name) for name in logging.root.manager.loggerDict]:
            structure_logger(logger)

        # Allow for Celery logs to report log level to Datadog
        # TODO - remove this once Celery log configuration hooks are sorted
        patch_celery_get_logger()

    def _process_request(self):
        """
        Authenticate every incoming request.
        """
        # Allow any OPTIONS request so CORS works properly
        if request.method == 'OPTIONS':
            return

        # Add Domo session to Datadog traces if provided
        if 'domo-session' in request.headers:
            span = tracer.current_span()
            if span:
                span.set_tags({'dh_potluck.domo.session': request.headers.get('domo-session')})
        return get_user(self._app_token, self._validate_token_func)

    def _process_response(self, response):
        """
        Capture SQL queries made during request and log info about them.
        """
        if os.environ.get('FLASK_DEBUG', 'false') == 'true':
            message = get_database_queries_summary(self._app)
            self._app.logger.info(message)

        return response

    def _register_error_handlers(self):
        # Catch flask-smorest validation errors and return them in JSON format
        @self._app.errorhandler(HTTPStatus.UNPROCESSABLE_ENTITY)
        def handle_unprocessable_entity(error):
            add_request_params_to_trace()
            response = {
                'description': 'Input failed validation.',
                'errors': error.exc.messages,
            }
            return jsonify(response), HTTPStatus.BAD_REQUEST

        # Catch marshmallow validation errors and return them in JSON format
        @self._app.errorhandler(ValidationError)
        def handle_validation_error(error):
            add_request_params_to_trace()
            response = {
                'description': 'Input failed validation.',
                'errors': error.messages,
            }
            return jsonify(response), HTTPStatus.BAD_REQUEST

        # Catch SQLAlchemy IntegrityErrors (usually unique constraint violations) and return them
        # in JSON format. TODO: Right now we return the database error as-is to the client. This
        # should be expanded to parse the integrity error and try to build a more structured,
        # user-friendly message about the error.
        @self._app.errorhandler(IntegrityError)
        def handle_integrity_errors(error):
            add_request_params_to_trace()
            return (
                jsonify({'description': f'Database integrity error: {error.orig.args[1]}'}),
                HTTPStatus.BAD_REQUEST,
            )

        # Ensure all other Flask HTTP exceptions are returned in JSON format
        @self._app.errorhandler(HTTPException)
        def handle_flask_exceptions(error):
            add_request_params_to_trace()
            return jsonify({'description': error.description}), error.code

        # Add extra context to Datadog traces for server errors
        @self._app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
        def handle_server_error(error):
            add_request_params_to_trace()
            error_response = (
                jsonify({'description': InternalServerError.description}),
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
            return error_response

        # Add extra context to Datadog traces for rate limited requests
        @self._app.errorhandler(HTTPStatus.TOO_MANY_REQUESTS)
        def handle_too_many_requests(error):
            if 'Authorization' in request.headers:
                key = self._get_rate_limit_key()
                cleaned_key = f'{key[0:4]}...{key[-4:-1]}'
            else:
                cleaned_key = request.remote_addr

            tracer.set_tags({'rate_limit_key': cleaned_key})

            return (
                jsonify(
                    {
                        'description': (
                            'The user has sent too many requests in a given amount of time.'
                        )
                    }
                ),
                HTTPStatus.TOO_MANY_REQUESTS,
            )

        @self._app.errorhandler(RemoteDisconnected)
        def handle_remote_disconnected_exception(error):
            add_request_params_to_trace()
            return (
                jsonify(
                    {
                        'description': (
                            'Remote Disconnected: Remote end closed connection without response.'
                        )
                    }
                ),
                HTTPStatus.SERVICE_UNAVAILABLE,
            )

        @self._app.errorhandler(HTTPStatus.NOT_FOUND)
        def page_not_found(e):
            """Don't return 404 on OPTIONS calls"""
            if request and request.method == 'OPTIONS':
                return '', HTTPStatus.OK

            error_response = (
                jsonify({'description': e.description}),
                HTTPStatus.NOT_FOUND,
            )

            return error_response

        @self._app.errorhandler(PlatformConnectionError)
        def handle_platform_connection_error(err):
            return jsonify({'description': str(err)}), HTTPStatus.BAD_REQUEST

        @self._app.errorhandler(Exception)
        def handle_error(e):
            # Catch and log unhandled exceptions in JSON format
            if self._structured_logging_enabled:
                extra = {
                    'error.stack': traceback.format_exc(),
                    'error.kind': str(type(e)),
                    'logger.thread_name': threading.Thread.getName(threading.current_thread()),
                }
                self._app.logger.error(str(e), extra=extra)
            else:
                traceback.print_exc()

            add_request_params_to_trace()
            return (
                jsonify({'description': InternalServerError.description}),
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )

    @staticmethod
    def role_required(*args, **kwargs):
        return role_required(*args, **kwargs)

    @property
    def current_user(self):
        return g.user

    @property
    def limiter(self):
        return self._limiter
