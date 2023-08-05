import logging
import time
import functools

def timelogger(func):
    @functools.wraps(func)
    def functimer(*args, **kwargs):
        logger = logging.getLogger(__name__)
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        logger.debug(f"{func.__qualname__!r} {run_time:.4f}s")
        return value
    return functimer
