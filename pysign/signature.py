import inspect
from typing import Callable, Tuple, List, Any, Mapping
from pysign.output import DEFAULT_OUTPUT, raise_assertion_error


def get_function_parameters(
    f: Callable,
) -> Tuple[Mapping[str, inspect.Parameter], type]:
    sign = inspect.signature(f)
    return sign.parameters, sign.return_annotation


def check_arg_typing(param: inspect.Parameter, arg: Any) -> Tuple[bool, str]:
    annotation = param.annotation
    if annotation == inspect.Parameter.empty:
        ret_val = True
    else:
        ret_val = isinstance(arg, annotation)

    if not ret_val:
        ret_msg = get_arg_wrong_typing_error_message(param, arg)
    else:
        ret_msg = ""

    return ret_val, ret_msg


def check_ret_typing(annotation: type, ret: Any) -> Tuple[bool, str]:
    if annotation == inspect.Parameter.empty:
        ret_val = True
    else:
        ret_val = isinstance(ret, annotation)

    if not ret_val:
        ret_msg = get_ret_wrong_typing_error_message(annotation, ret)
    else:
        ret_msg = ""

    return ret_val, ret_msg


def get_arg_wrong_typing_error_message(param: inspect.Parameter, arg: Any) -> str:
    return f"Argument `{param.name}` does not match typing: {repr(arg)} is not an instance of {param.annotation}"


def get_ret_wrong_typing_error_message(annotation: type, ret: Any) -> str:
    return f"Return value does not match typing: {repr(ret)} is not an instance of {annotation}"


def check_args_typing(params: Mapping[str, inspect.Parameter], *args: Any, **kwargs):
    checks = []

    for param, arg in zip(params.values(), args):
        checks.append(check_arg_typing(param, arg))

    for key, arg in kwargs.items():
        checks.append(check_arg_typing(params[key], arg))

    return checks


def output_if_arg_incorrect_typing(
    param: inspect.Parameter, arg: Any, output: Callable = DEFAULT_OUTPUT
) -> None:
    ret_val, ret_msg = check_arg_typing(param, arg)
    if not ret_val:
        output(ret_msg)


def output_if_ret_incorrect_typing(
    annotation: type, ret: Any, output: Callable = DEFAULT_OUTPUT
) -> None:
    ret_val, ret_msg = check_ret_typing(annotation, ret)
    if not ret_val:
        output(ret_msg)


def output_if_args_incorrect_typing(
    params: Mapping[str, inspect.Parameter],
    *args: Any,
    join: bool = True,
    output: Callable = DEFAULT_OUTPUT,
    **kwargs: Any,
) -> None:
    checks = check_args_typing(params, *args, **kwargs)

    if join:
        success = True
        failed = []

        for ret_val, ret_msg in checks:
            success &= ret_val

            if not ret_val:
                failed.append(ret_msg)

        if not success:
            output("\n".join(failed))

    else:
        for ret_val, ret_msg in checks:
            if not ret_val:
                output(ret_msg)


def assert_arg_correct_typing(param: inspect.Parameter, arg: Any) -> None:
    return output_if_arg_incorrect_typing(param, arg, output=raise_assertion_error)


def assert_ret_correct_typing(annotation: type, ret: Any) -> None:
    return output_if_ret_incorrect_typing(annotation, ret, output=raise_assertion_error)


def assert_args_correct_typing(
    params: Mapping[str, inspect.Parameter],
    *args: Any,
    join: bool = True,
    **kwargs: Any,
) -> None:
    return output_if_args_incorrect_typing(
        params, *args, join=join, output=raise_assertion_error, **kwargs
    )
