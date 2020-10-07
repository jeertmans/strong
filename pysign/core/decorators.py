from pysign.core.signature import (
    get_function_parameters,
    get_function_context,
    output_if_args_incorrect_typing,
    output_if_ret_incorrect_typing,
)
from pysign.utils.output import (
    DEFAULT_OUTPUT,
    raise_assertion_error,
    raise_warning,
)
from typing import Callable, Any, Optional, Mapping
from timeit import timeit, Timer
import functools


def check_correct_typing(
    func: Optional[Callable] = None,
    join: bool = True,
    output: Callable = DEFAULT_OUTPUT,
) -> Callable:
    def _check_correct_typing(func):
        args_mapping, out_type = get_function_parameters(func)
        context = get_function_context(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            output_if_args_incorrect_typing(
                args_mapping, args, kwargs, join=join, output=output, context=context
            )

            result = func(*args, **kwargs)

            output_if_ret_incorrect_typing(out_type, result, output=output)

            return result

        return wrapper

    if func is not None:
        return _check_correct_typing(func)
    else:
        return _check_correct_typing


def assert_correct_typing(
    func: Optional[Callable] = None, join: bool = True
) -> Callable:
    return check_correct_typing(func=func, join=join, output=raise_assertion_error)


def warn_if_incorrect_typing(
    func: Optional[Callable] = None, join: bool = True
) -> Callable:
    return check_correct_typing(func=func, join=join, output=raise_warning)


def measure_overhead(
    func: Optional[Callable] = None,
    decorator: Optional[Callable] = None,
    dec_kwargs: Optional[Mapping[str, Any]] = None,
) -> Callable:
    if dec_kwargs is None:
        dec_kwargs = dict()

    if decorator is None:
        decorator = func
        func = None

    def _measure_overhead(func):

        wrapped = decorator(func=func, **dec_kwargs)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            n, t_std = Timer(lambda: func(*args, **kwargs)).autorange()
            t_wrp = timeit(lambda: wrapped(*args, **kwargs), number=n)
            return t_wrp / t_std

        return wrapper

    if func is not None:
        return _measure_overhead(func)
    else:
        return _measure_overhead


if __name__ == "__main__":

    import numpy as np
    from typing import Union

    @measure_overhead(assert_correct_typing)
    def f(a: int, b: int) -> np.ndarray:
        return np.random.rand(a, a) + b

    @assert_correct_typing
    def g(a: int, b: int) -> int:
        return a + b


    def h(a: int, b: int) -> int:
        return a + b

    h2 = assert_correct_typing(h)

    h2(2.0, 1)
    g(1, 1.0)
    print(f(100, 100))
