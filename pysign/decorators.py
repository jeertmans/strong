from pysign.signature import get_function_parameters, assert_args_correct_typing, assert_ret_correct_typing
from itertools import chain


def assert_correct_typing(func):
    args_signature, out_type = get_function_parameters(func)

    def wrap(*args, **kwargs):

        all_args = chain(args, kwargs.values())

        assert_args_correct_typing(args_signature, all_args)

        result = func(*args, **kwargs)

        assert_ret_correct_typing(out_type, result)

        return result

    return wrap
