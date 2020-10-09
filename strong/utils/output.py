import warnings
import sys


def raise_warning(msg: str) -> None:
    """
    Raises a warning with given message.

    :param msg: the message

    :Example:

    >>> raise_warning("Hello")
    Warning: Hello
    """
    warnings.warn(msg, Warning)


def raise_assertion_error(msg: str) -> None:
    """
    Raises an assertion error with given message.

    :param msg: the message
    :raises: AssertionError

    :Example:

    >>> raise_assertion_error("Hello")
    AssertionError: Hello
    """
    raise AssertionError(msg)


def raise_type_error(msg: str) -> None:
    """
    Raises a type error with given message.

    :param msg: the message
    :raises: TypeError

    :Example:

    >>> raise_type_error("Hello")
    TypeError: Hello
    """
    raise TypeError(msg)


def raise_stdout(msg: str) -> None:
    """
    Prints a message in the standard output.

    :param msg: the message

    :Example:

    >>> raise_stdout("Hello")
    Hello
    """
    print(msg)


def raise_stderr(msg: str) -> None:
    """
    Prints a message in the error output.

    :param msg: the message

    :Example:

    >>> raise_stderr("Hello")
    Hello  # in red
    """
    print(msg, file=sys.stderr)


DEFAULT_OUTPUT = raise_stderr
