import warnings
import sys


def raise_warning(msg):
    warnings.warn(msg, Warning)


def raise_assertion_error(msg):
    raise AssertionError(msg)


def raise_attribute_error(msg):
    raise AttributeError(msg)


def raise_stdout(msg):
    print(msg)


def raise_stderr(msg):
    print(msg, file=sys.stderr)
