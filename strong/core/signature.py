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
    Callable,
)
from strong.utils.output import DEFAULT_OUTPUT, raise_assertion_error
from collections.abc import Mapping as abcMapping, Callable as abcCallable


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


def check_obj_typing(annotation: type, obj: Any) -> bool:
    """
    Returns True if the object matches a given type.
    An object matches a type if it can be considered to be an instance of
    given type.

    :param annotation: the type annotation
    :param obj: the object
    :return: True if object matches given type

    :Example:

    >>> from typing import Union
    >>> check_obj_typing(Union[int, float], 1)
    True
    """
    origin = getattr(annotation, "__origin__", None)

    if origin is not None:
        args = getattr(annotation, "__args__", None)
        nargs = len(args)

        if type(origin) == type(Union):

            return any(check_obj_typing(t, obj) for t in args)

        elif isinstance(obj, origin):
            if origin == Tuple or origin == tuple:
                if len(obj) != nargs:
                    return False
                else:
                    return all(
                        check_obj_typing(t, o) for t, o in zip(args, obj)
                    )
            elif origin == List or origin == list:
                return all(check_obj_typing(args[0], o) for o in obj)
            elif (
                origin == Mapping
                or origin == abcMapping
                or origin == Dict
                or origin == dict
            ):
                return all(
                    check_obj_typing(args[0], o) for o in obj.keys()
                ) and all(check_obj_typing(args[1], o) for o in obj.values())
            elif origin == Set or origin == set:
                return all(check_obj_typing(args[0], o) for o in obj)
            elif origin == Callable or origin == abcCallable:
                params, annotation = get_function_parameters(obj)
                return (
                    check_obj_typing(args[-1], annotation)
                    and len(args[:-1]) == len(params)
                    and all(
                        check_obj_typing(arg, param.annotation)
                        for arg, param in zip(args[:-1], params.values())
                    )
                )
            else:
                raise NotImplementedError(
                    "Type %s is currently "
                    "not "
                    "supported. Please post an issue "
                    "on "
                    "the github so that we can quickly "
                    "fix it: "
                    "https://github.com/jeertmans"
                    "/strong/issues" % annotation
                )
        else:
            return False
    else:
        if annotation == Any:
            return True
        elif type(obj) == type:
            return issubclass(obj, annotation)
        else:
            return isinstance(obj, annotation)


def check_arg_typing(param: inspect.Parameter, arg: Any) -> Tuple[bool, str]:
    """
    Returns True if input argument matches given parameter type.
    Otherwise return False and an error message.
    See :func:`check_obj_typing` for more information.

    :param param: the parameter
    :param arg: the input argument
    :return: True if argument matches parameter type
    """
    annotation = param.annotation
    if annotation == inspect.Parameter.empty:
        ret_val = True
    else:
        ret_val = check_obj_typing(annotation, arg)

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
    if annotation == inspect.Parameter.empty:
        ret_val = True
    else:
        ret_val = check_obj_typing(annotation, ret)

    if not ret_val:
        ret_msg = get_ret_wrong_typing_error_message(annotation, ret)
    else:
        ret_msg = ""

    return ret_val, ret_msg


def get_arg_wrong_typing_error_message(
    param: inspect.Parameter, arg: Any
) -> str:
    """
    Builds a message for a wrong argument typing error.

    :param param: the parameter
    :param arg: the input argument
    :return: the message
    """
    return (
        "Argument `%s` does not match typing:"
        "%s is not an instance of %s"
        % (
            param.name,
            repr(arg),
            param.annotation,
        )
    )


def get_ret_wrong_typing_error_message(annotation: type, ret: Any) -> str:
    """
    Builds a message for a wrong return value typing error.

    :param annotation: the type
    :param ret: the return value
    :return: the message
    """
    return (
        "Return value does not match typing:"
        "%s is not an instance of %s"
        % (
            repr(ret),
            annotation,
        )
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


def assert_ret_correct_typing(
    annotation: type, ret: Any, context: str = ""
) -> None:
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
