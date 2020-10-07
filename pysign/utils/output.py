import warnings
import sys


def raise_warning(msg: str) -> None:
    """
    Raises a warning with given message.

    :param msg: the message
    """
    warnings.warn(msg, Warning)


def raise_assertion_error(msg: str) -> None:
    """
    Raises an assertion error with given message.

    :param msg: the message
    :raises: AssertionError
    """
    raise AssertionError(msg)


def raise_type_error(msg: str) -> None:
    """
    Raises a type error with given message.

    :param msg: the message
    :raises: TypeError
    """
    raise TypeError(msg)


def raise_stdout(msg: str) -> None:
    """
    Prints a message in the standard output.

    :param msg: the message
    """
    print(msg)


def raise_stderr(msg: str) -> None:
    """
    Prints a message in the error output.

    :param msg: the message
    """
    print(msg, file=sys.stderr)


DEFAULT_OUTPUT = raise_stderr
