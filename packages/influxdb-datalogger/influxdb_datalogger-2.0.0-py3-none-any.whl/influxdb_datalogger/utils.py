from concurrent.futures import ThreadPoolExecutor
from typing import *


def threaded_execution(target: Callable, *args_as_iterable: Union[Set, List, Tuple, KeysView, ItemsView, ValuesView], pool_size: int = None):
    """
    Function to wrap ThreadedExecutor. Takes a function and arguments as an iterable and creates
    an executor pool to run the function concurrently.
    Args:
        target: A callable that takes each value in 'args_as_iterable' as an argument.
        args_as_iterable: An iterable where arguments for 'target' is in each element in the iterable.
        pool_size: Optional argument for setting the size of the thread pool. Default is None, in which case len(args_as_iterable) will be used as pool size. If set to 0, pool_size will effectively unlimited.
    Returns:
        A list with the return values from 'target'.
    """
    class ThreadedExecutor(object):
        def __init__(self, size=10):
            self.executor = ThreadPoolExecutor(max_workers=size)
            self.map = self.executor.map

        def __enter__(self):
            def nonlazy_map(function, *iterable_args):
                return list(self.map(function, *iterable_args))
            return nonlazy_map

        def __exit__(self, exc_type, exc_val, exc_tb):
            if hasattr(self, 'executor'):
                self.executor.shutdown()

    zipped = list(zip(*args_as_iterable))
    if len(zipped) == 0:
        return

    # Set pool_size to pool_size if it was configured, otherwise use len(args_as_iterable)
    pool_size = pool_size or len(zipped)

    assert isinstance(pool_size, int)
    with ThreadedExecutor(size=pool_size) as threaded_executor_function:
        _ret = threaded_executor_function(target, *args_as_iterable)
        return _ret