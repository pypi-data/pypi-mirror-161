import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)


def retry(
    exceptions=Exception,
    tries=4,
    delay=3,
    backoff=2,
    custom_logger=None,
    verbose=False,
    skip_exceptions=False,
    do_retry_func=None,
):
    """
    Retry calling the decorated function using an exponential backoff.

    :param exceptions: the exception to check. may be a tuple of exceptions to check
    :param tries: number of times to try (not retry) before giving up
    :param delay: initial delay between retries in seconds
    :param backoff: backoff multiplier e.g. value of 2 will double the delay each retry
    :param custom_logger: logger to use. If None, print
    :param verbose: Indicates if the stacktrace should be logged on the first retry
    :param skip_exceptions: Shows whether exceptions will be skipped or not after all tries
    :param do_retry_func: Function that determines if we should retry given the exception
    :return:
    """

    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            try_number = 1
            wait_time = delay
            mlogger = custom_logger if custom_logger else logger
            log_stacktrace = verbose

            while try_number < tries:
                try:
                    return f(*args, **kwargs)
                except exceptions as e:
                    if do_retry_func and not do_retry_func(e):
                        mlogger.info('No more retries')
                        if not skip_exceptions:
                            raise e

                    remaining = tries - try_number
                    mlogger.warning(
                        f'{e}, Retrying in {wait_time:.1f} seconds ... (remaining={remaining})',
                        exc_info=log_stacktrace,
                    )

                    time.sleep(wait_time)

                    try_number += 1
                    wait_time = delay * backoff**try_number
                    log_stacktrace = False

            try:
                return f(*args, **kwargs)
            except exceptions as e:
                mlogger.warning('All retries exhausted, terminating.')
                if not skip_exceptions:
                    raise e

        return f_retry  # true decorator

    return deco_retry
