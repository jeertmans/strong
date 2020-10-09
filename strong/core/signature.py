import inspect
from typing import Callable, Tuple, Union, Any, Mapping, List, Dict, Set
from strong.utils.output import DEFAULT_OUTPUT, raise_assertion_error


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
    'Function f defined in "<path>", line <lineno>'
    """
    name = f.__name__

    file = inspect.getsourcefile(f)
    try:
        lineno = inspect.getsourcelines(f)[1]
    except OSError:
        lineno = "<SourceCodeCannotBeRetrieved>"
    return f'Function {name} defined in "{file}", line {lineno}'


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
            if origin == Tuple:
                if len(obj) != nargs:
                    return False
                else:
                    return all(
                        check_obj_typing(t, o) for t, o in zip(args, obj)
                    )
            elif origin == List:
                return all(check_obj_typing(args[0], o) for o in obj)
            elif origin == Mapping or origin == Dict:
                return all(
                    check_obj_typing(args[0], o) for o in obj.keys()
                ) and all(check_obj_typing(args[1], o) for o in obj.values())
            elif origin == Set:
                return all(check_obj_typing(args[0], o) for o in obj)
            else:
                raise NotImplementedError(
                    f"Type {annotation} is currently "
                    f"not "
                    f"supported. Please post an issue "
                    f"on "
                    f"the github so that we can quickly "
                    f"fix it: "
                    f"https://github.com/jeertmans"
                    f"/strong/issues"
                )
        else:
            return False
    else:
        if annotation == Any:
            return True
        else:
            return isinstance(obj, annotation)


def check_arg_typing(param: inspect.Parameter, arg: Any) -> Tuple[bool, str]:
    """
    Returns True if input argument matches given parameter type.
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
    return (
        f"Argument `{param.name}` does not match typing:"
        f"{repr(arg)} is not an instance of {param.annotation}"
    )


def get_ret_wrong_typing_error_message(annotation: type, ret: Any) -> str:
    return (
        f"Return value does not match typing:"
        f"{repr(ret)} is not an instance of {annotation}"
    )


def get_message_with_context(msg: str, context: str) -> str:
    if len(context) == 0:
        return msg
    else:
        msg = "\t" + "\n\t".join(msg.splitlines())
        return f"{context}\n{msg}"


def check_args_typing(
    params: Mapping[str, inspect.Parameter], *args: Any, **kwargs
) -> List[Tuple[bool, str]]:
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
    return output_if_arg_incorrect_typing(
        param, arg, output=raise_assertion_error, context=context
    )


def assert_ret_correct_typing(
    annotation: type, ret: Any, context: str = ""
) -> None:
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
    return output_if_args_incorrect_typing(
        params,
        args,
        kwargs,
        join=join,
        output=raise_assertion_error,
        context=context,
    )
