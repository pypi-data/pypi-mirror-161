import time
from functools import wraps


def retry(tries=3, delay=3, backoff=2, logger=None, should_retry=None):
    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    :param should_retry: check if retry should be called
    :type should_retry: function object
    """
    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            # print(args)
            # print(kwargs)

            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    # remove logging potential user sensitive information
                    error_code = getattr(e, 'error_code', '')
                    if should_retry is not None and should_retry(e):
                        msg = "%s, Retrying in %d seconds..." % (error_code, mdelay)
                        if logger:
                            logger.warning(msg)
                        else:
                            print(msg)
                        time.sleep(mdelay)
                        mtries -= 1
                        mdelay *= backoff
                    else:
                        # Otherwise raise the error directly
                        raise e
            return f(*args, **kwargs)

        return f_retry  # true decorator
    return deco_retry
