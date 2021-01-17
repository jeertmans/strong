from strong.core.signature import (
    get_function_parameters,
    get_function_context,
    output_if_args_incorrect_typing,
    output_if_ret_incorrect_typing,
)
from strong.utils.output import (
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
    """
    Wraps a function while outpouting error(s) if the arguments and
    output are incorrectly typed.

    :param func: the function
    :param join: if True, will join all errors and raise them at once
    :param output: the desired output (see utils.output module)
    :return: the function wrapped
    """

    def _check_correct_typing(func):
        args_mapping, out_type = get_function_parameters(func)
        context = get_function_context(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            output_if_args_incorrect_typing(
                args_mapping,
                args,
                kwargs,
                join=join,
                output=output,
                context=context,
            )

            result = func(*args, **kwargs)

            output_if_ret_incorrect_typing(
                out_type, result, output=output, context=context
            )

            return result

        return wrapper

    if func is not None:
        return _check_correct_typing(func)
    else:
        return _check_correct_typing


def assert_correct_typing(
    func: Optional[Callable] = None, join: bool = True
) -> Callable:
    """
    Applies :func:`check_correct_typing` with assertion error as output.

    :param func: the function
    :param join: if True, will join all errors and raise them at once
    :return: the function wrapped

    :Example:

    >>> from strong.core.decorators import assert_correct_typing
    >>> @assert_correct_typing
    >>> def f(a: int, b: int) -> int:
    >>>     return a + b
    >>> x = f(1, 2)    # O.K.
    >>> y = f(1, '2')  # K.O.
    AssertionError: Function f defined in "<function_file>", line 3
        Argument `b` does not match typing: '2' is not an instance of
        <class 'int'>
    """
    return check_correct_typing(func=func, join=join, output=raise_assertion_error)


def warn_if_incorrect_typing(
    func: Optional[Callable] = None, join: bool = True
) -> Callable:
    """
    Applies :func:`check_correct_typing` with warning as output.

    :param func: the function
    :param join: if True, will join all errors and raise them at once
    :return: the function wrapped
    """
    return check_correct_typing(func=func, join=join, output=raise_warning)


def measure_overhead(
    func: Optional[Callable] = None,
    decorator: Optional[Callable] = None,
    dec_kwargs: Optional[Mapping[str, Any]] = None,
) -> Callable:
    """
    Returns the overhead time ratio between a function call with
    @decorator and without.

    :param func: the function
    :param decorator: the decorator which will be measured
    :param dec_kwargs: optional keyword-arguments to be passed to the decorator
    :return: a function computing the overhead time ratio, i.e. time
        (with dec.) / time (without dec.)

    :Example:

    >>> from strong.core.decorators import (
    >>> assert_correct_typing,
    >>> measure_overhead,
    >>> )
    >>> import numpy as np
    >>> @measure_overhead(assert_correct_typing)
    >>> def g(a: int, b: int) -> np.ndarray:
    >>>    return np.random.rand(a, b)
    >>> g(100, 100)
    1.0687804670719938  # Ratio between time taken with
                        # @assert_correct_typing and without
    """
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
