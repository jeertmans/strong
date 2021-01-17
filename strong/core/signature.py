import inspect
from typing import (
    Callable,
    Tuple,
    Union,
    Any,
    Mapping,
    List,
    Dict,
    Set,
    Type,
)
from typing import (
    Any,
    Callable,
    Union,
    Tuple,
    Type,
    get_type_hints,
    get_origin,
    get_args,
)
from collections import abc

from strong.utils.output import DEFAULT_OUTPUT, raise_assertion_error


def annotation_to_type(annotation: type) -> type:
    if annotation == inspect.Parameter.empty:
        return Any
    else:
        return annotation


def get_function_parameters(
    f: Callable,
) -> Tuple[Mapping[str, inspect.Parameter], type]:
    """
    Returns function's signature as parameters and the output type.

    :param f: the function
    :return: the parameters and the output type
    :raises: ValueError: if the function is a builtin function or method

    :Example:

    >>> def f(a: int, b: int) -> int:
    >>>     return a + b
    >>> get_function_parameters(f)
    (mappingproxy({'a': <Parameter "a:int">, 'b': <Parameter "b:int">}), int)
    """
    sign = inspect.signature(f)
    return sign.parameters, sign.return_annotation


def get_function_type_hints(
    f: Callable,
) -> Tuple[List[type], type]:
    """
    Returns function's type hints as parameters types and the output type.

    :param f: the function
    :return: the parameters types and the output type
    :raises: ValueError: if the function is a builtin function or method

    :Example:

    >>> def f(a: int, b: int) -> int:
    >>>     return a + b
    >>> get_function_parameters(f)
    ([int, int], int)
    """
    args, ret = get_function_parameters(f)
    ret = annotation_to_type(ret)

    args = [annotation_to_type(arg.annotation) for arg in args.values()]

    return args, ret


def get_function_context(f: Callable) -> str:
    """
    Returns the function's context, containing:
    * its name
    * the location of its code
    * the first line of its code (if exists)

    :param f: the function
    :return: the context
    :raises: TypeError: if the function is a builtin function or method

    :Example:

    >>> def f(a: int, b: int) -> int:
    >>>     return a + b
    >>> get_function_context(f)
    "<stdin>:1:f"
    """
    name = f.__qualname__

    file = inspect.getsourcefile(f)
    try:
        lineno = inspect.getsourcelines(f)[1]
    except OSError:
        lineno = "<SourceCodeCannotBeRetrieved>"

    return "%s:%d:%s" % (file, lineno, name)


_TAGS_ = dict()
_TAG_FUNCTION_SIGNATURE_ = {"x": Any, "args": type, "return": bool}


def tag(*tags: type) -> Callable:
    """
    Wrapper that will add current function as reference to know is an object is
    instance of tagged types.

    :param tags:
    :return:
    """

    def _tag_(func):
        assert (
            get_type_hints(func) == _TAG_FUNCTION_SIGNATURE_
        ), f"Function {func} must exactly have this signature: {_TAG_FUNCTION_SIGNATURE_}"
        for _tag in tags:
            _TAGS_[_tag] = func

        return func

    return _tag_


def _issubclass_(a: type, b: type) -> bool:
    if a is Any:
        return a
    elif b is Any:
        return False
    else:
        return issubclass(a, b)


@tag(Any)
def _any_(x: Any, *args: type) -> bool:
    return True


@tag(Callable, abc.Callable)
def _callable_(x: Any, *args: type) -> bool:
    if not isinstance(x, Callable):
        return False
    if args:
        arg_tps = args[0]
        ret_tp = args[1]
        args, ret = get_function_type_hints(x)
        return (
            len(args) == len(arg_tps)
            and all(_issubclass_(arg_tp, arg) for arg, arg_tp in zip(args, arg_tps))
            and _issubclass_(ret_tp, ret)
        )
    return True


@tag(Tuple, tuple)
def _tuple_(x: Any, *args: type) -> bool:
    return isinstance(x, tuple) and len(x) == len(args)


@tag(Type, type)
def _type_(x: Any, *args: type) -> bool:
    return check_obj_typing(x, args[0])


@tag(Union)
def _union_(x: Any, *args: type) -> bool:
    return any(check_obj_typing(x, tp) for tp in args)


def check_obj_typing(obj: Any, tp: type) -> bool:
    """
    Returns True if the object matches a given type.
    An object matches a type if it can be considered to be an instance of
    given type.

    :param obj: the object
    :param tp: the type annotation
    :return: True if object matches given type

    :Example:

    >>> from typing import Union
    >>> check_obj_typing(1, Union[int, float])
    True
    """
    origin, args = get_origin(tp), get_args(tp)
    if origin is None:
        origin = tp
    if origin in _TAGS_:
        return _TAGS_[origin](obj, *args)
    else:
        print(obj, origin)
        return isinstance(obj, origin)


def check_arg_typing(param: inspect.Parameter, arg: Any) -> Tuple[bool, str]:
    """
    Returns True if input argument matches given parameter type.
    Otherwise return False and an error message.
    See :func:`check_obj_typing` for more information.

    :param param: the parameter
    :param arg: the input argument
    :return: True if argument matches parameter type
    """
    tp = annotation_to_type(param.annotation)
    ret_val = check_obj_typing(arg, tp)

    if not ret_val:
        ret_msg = get_arg_wrong_typing_error_message(param, arg)
    else:
        ret_msg = ""

    return ret_val, ret_msg


def check_ret_typing(annotation: type, ret: Any) -> Tuple[bool, str]:
    """
    Returns True if return value matches given parameter type.
    Otherwise return False and an error message.
    See :func:`check_obj_typing` for more information.

    :param annotation: the type
    :param ret: the return value
    :return: True if argument matches parameter type
    """
    tp = annotation_to_type(annotation)
    ret_val = check_obj_typing(ret, tp)

    if not ret_val:
        ret_msg = get_ret_wrong_typing_error_message(annotation, ret)
    else:
        ret_msg = ""

    return ret_val, ret_msg


def get_arg_wrong_typing_error_message(param: inspect.Parameter, arg: Any) -> str:
    """
    Builds a message for a wrong argument typing error.

    :param param: the parameter
    :param arg: the input argument
    :return: the message
    """
    return "Argument `%s` does not match typing:" "%s is not an instance of %s" % (
        param.name,
        repr(arg),
        param.annotation,
    )


def get_ret_wrong_typing_error_message(annotation: type, ret: Any) -> str:
    """
    Builds a message for a wrong return value typing error.

    :param annotation: the type
    :param ret: the return value
    :return: the message
    """
    return "Return value does not match typing:" "%s is not an instance of %s" % (
        repr(ret),
        annotation,
    )


def get_message_with_context(msg: str, context: str) -> str:
    """
    Concatenates an error message with a context. If context is empty
    string, will only return the error message.

    :param msg: the message
    :param context: the context of the message
    :return: the message with context
    """
    if len(context) == 0:
        return msg
    else:
        msg = "\t" + "\n\t".join(msg.splitlines())
        return "%s\n%s" % (context, msg)


def check_args_typing(
    params: Mapping[str, inspect.Parameter], *args: Any, **kwargs: Any
) -> List[Tuple[bool, str]]:
    """
    Returns a list of (bool, message) pairs for each input argument.
    See :func:`check_arg_typing` for more information.
    If a keyword argument is invalid, it will be skipped.
    Same applies if to many arguments are given.

    :param params: the parameters
    :param args: the input positional arguments
    :param kwargs: the input keyword arguments
    :return: a list of (bool, message) pairs
    """
    checks = []

    for param, arg in zip(params.values(), args):
        checks.append(check_arg_typing(param, arg))

    for key, arg in kwargs.items():
        try:
            checks.append(check_arg_typing(params[key], arg))
        except KeyError:
            # If invalid keyword argument,
            # will let the error be raised by Python
            pass

    return checks


def output_if_arg_incorrect_typing(
    param: inspect.Parameter,
    arg: Any,
    output: Callable = DEFAULT_OUTPUT,
    context: str = "",
) -> None:
    """
    Outputs an error message if input argument doesn't matches given parameter
    type.
    See :func:`check_arg_typing` for more information.

    :param param: the parameter
    :param arg: the input argument
    :param output: the desired output (see utils.output module)
    :param context: the context of the message
    """
    ret_val, ret_msg = check_arg_typing(param, arg)
    if not ret_val:
        ret_msg = get_message_with_context(ret_msg, context)
        output(ret_msg)


def output_if_ret_incorrect_typing(
    annotation: type,
    ret: Any,
    output: Callable = DEFAULT_OUTPUT,
    context: str = "",
) -> None:
    """
    Outputs an error message if return value doesn't matches given parameter
    type.
    See :func:`check_ret_typing` for more information.

    :param annotation: the type
    :param ret: the return value
    :param output: the desired output (see utils.output module)
    :param context: the context of the message
    """
    ret_val, ret_msg = check_ret_typing(annotation, ret)
    if not ret_val:
        ret_msg = get_message_with_context(ret_msg, context)
        output(ret_msg)


def output_if_args_incorrect_typing(
    params: Mapping[str, inspect.Parameter],
    args: Tuple[Any],
    kwargs: Mapping[str, Any],
    join: bool = True,
    output: Callable = DEFAULT_OUTPUT,
    context: str = "",
) -> None:
    """
    Outputs an error message if any input argument doesn't matches given
    parameter
    type.
    See :func:`check_args_typing` for more information.

    :param params: the parameter
    :param args: the input positional arguments
    :param kwargs:  the input keyword arguments
    :param join: if True, will join all the errors in one
    :param output: the desired output (see utils.output module)
    :param context: the context of the message
    """
    checks = check_args_typing(params, *args, **kwargs)

    if join:
        success = True
        failed = []

        for ret_val, ret_msg in checks:
            success &= ret_val

            if not ret_val:
                failed.append(ret_msg)

        if not success:
            ret_msg = get_message_with_context("\n".join(failed), context)
            output(ret_msg)

    else:
        for ret_val, ret_msg in checks:
            if not ret_val:
                ret_msg = get_message_with_context(ret_msg, context)
                output(ret_msg)


def assert_arg_correct_typing(
    param: inspect.Parameter, arg: Any, context: str = ""
) -> None:
    """
    Applies :func:`output_if_arg_incorrect_typing` with assertion error as
    output.

    :param param: the parameter
    :param arg: the input argument
    :param context: the context of the message
    """
    return output_if_arg_incorrect_typing(
        param, arg, output=raise_assertion_error, context=context
    )


def assert_ret_correct_typing(annotation: type, ret: Any, context: str = "") -> None:
    """
    Applies :func:`output_if_ret_incorrect_typing` with assertion error as
    output.

    :param annotation: the type
    :param ret: the return value
    :param context: the context of the message
    """
    return output_if_ret_incorrect_typing(
        annotation, ret, output=raise_assertion_error, context=context
    )


def assert_args_correct_typing(
    params: Mapping[str, inspect.Parameter],
    args: Tuple[Any],
    kwargs: Mapping[str, Any],
    join: bool = True,
    context: str = "",
) -> None:
    """
    Applies :func:`output_if_args_incorrect_typing` with assertion error as
    output.

    :param params: the parameter
    :param args: the input positional arguments
    :param kwargs:  the input keyword arguments
    :param join: if True, will join all the errors in one
    :param context: the context of the message
    """
    return output_if_args_incorrect_typing(
        params,
        args,
        kwargs,
        join=join,
        output=raise_assertion_error,
        context=context,
    )
