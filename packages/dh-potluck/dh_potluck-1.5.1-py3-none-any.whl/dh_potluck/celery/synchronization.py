from typing import Optional


class SemaphoreLocked(Exception):
    pass


try:
    from redis import Redis

    class Semaphore(object):
        """
        Class allowing using Redis backend for task synchronization

        Synopsis:

        redis = Redis(host=..., port=..., db=...)

        # mutual exclusivity (mutex) to perform operation on a foo resource
        @celery.task
        def a_task(foo, bar):
            with Semaphore(redis, 'mutex'+foo, 60):
                # now I have exclusive access to for 60 seconds to 'foo' resource
                do_the_job()
            except MutexTaken:
                # some other task is already using the resource so I skip
                pass

        # optionally restrict to only N concurrent operations on a specific task, regardless of the
        # task capacity (warning, will be blocking tasks waiting on execution)

        def optional_limited_capacity():
            if not Config.MAX_CONCURRENT_RUNNING_TASKS:
                # always allowing entering the resource
                return Semaphore.dummy()
            return Semaphore(redis, 'throttled_resource', 3600, Config.MAX_CONCURRENT_RUNNING_TASKS)

        @celery.task
        def throttled_task(foo, bar):
            while True:
                with optional_limited_capacity():
                    # now I am one of N to do the work
                    do_the_job();
                    break;
                except MutexTaken:
                    time.sleep(1) # not to hog server CPU

        """

        def __init__(
            self,
            redis_client: Optional[Redis],
            key_name: Optional[str],
            ttl: int,
            capacity: int = 1,
        ):
            if key_name is not None:
                current_value = int(redis_client.get(key_name) or 0)
                if current_value >= capacity:
                    raise SemaphoreLocked()
                current_value += 1
                redis_client.setex(key_name, time=ttl, value=current_value)
            self._key_name = key_name
            self._ttl = ttl
            self._client = redis_client

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if self._key_name is not None:
                current_value = int(self._client.get(self._key_name) or 0)
                current_value -= 1
                if current_value <= 0:
                    self._client.delete(self._key_name)
                else:
                    self._client.setex(self._key_name, time=self._ttl, value=current_value)

        @classmethod
        def dummy(cls) -> 'Semaphore':
            return Semaphore(None, None, 0)

except ModuleNotFoundError:
    pass
