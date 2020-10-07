from pysign.signature import (
    get_function_parameters,
    output_if_args_incorrect_typing,
    output_if_ret_incorrect_typing,
)
from pysign.output import DEFAULT_OUTPUT, raise_assertion_error
from typing import Callable


def check_correct_typing(
    func: Callable, join: bool = True, output: Callable = DEFAULT_OUTPUT
):
    args_mapping, out_type = get_function_parameters(func)

    def wrap(*args, **kwargs):
        output_if_args_incorrect_typing(
            args_mapping, *args, join=join, output=output, **kwargs
        )

        result = func(*args, **kwargs)

        output_if_ret_incorrect_typing(out_type, result, output=output)

        return result

    return wrap


def assert_correct_typing(func: Callable, join: bool = True):
    return check_correct_typing(func, join=join, output=raise_assertion_error)
