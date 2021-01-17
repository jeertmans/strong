import argparse
from pathlib import Path
import os
from strong.core.signature import get_function_parameters, get_function_context
import inspect
import importlib.util
import sys
from typing import Callable

IGNORE_ARGS = ["self", "cls"]

parser = argparse.ArgumentParser(
    description="Verifies that every function in every module is typed."
)

parser.add_argument(
    "input",
    metavar="INPUT",
    type=str,
    default=".",
    help="Python file or directory containing Python files to be analysed",
)


def check_function(f: Callable) -> None:
    parameters, out_type = get_function_parameters(f)

    header = get_function_context(f)

    for parameter_name, parameter_type in parameters.items():
        if (
            parameter_type.annotation == inspect.Parameter.empty
            and parameter_name not in IGNORE_ARGS
        ):
            print("%s: parameter `%s` is missing type-hint" % (header, parameter_name))
    if out_type == inspect.Parameter.empty:
        print("%s: return value is missing type-hint" % header)


def check_module(filename: str) -> None:
    module_name = inspect.getmodulename(filename)
    spec = importlib.util.spec_from_file_location(module_name, filename)
    module = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(module)
    except Exception:
        pass  # Some files like setup.py cannot be loaded...

    members = inspect.getmembers(module)
    module_path = inspect.getfile(module)

    def _check_members(obj, members, depth):

        if depth < 0:
            return

        for member_name, member_type in members:
            member = getattr(obj, member_name, None)

            if inspect.isfunction(member_type) and module_path == inspect.getfile(
                member_type
            ):
                check_function(member)
            elif inspect.isclass(member_type):
                _check_members(member, inspect.getmembers(member), depth - 1)

    _check_members(module, members, 1)


def main() -> None:
    args = parser.parse_args()
    if os.path.isfile(args.input):
        _, ext = os.path.splitext(args.input)
        if ext.lower() != ".py":
            raise TypeError("Strong can only handle Python files")
        else:
            check_module(args.input)
    elif os.path.isdir(args.input):
        if args.input != ".":
            sys.path.insert(0, os.path.abspath(args.input))
        for path in Path(args.input).rglob("*.py"):
            check_module(str(path))
    else:
        raise TypeError("`%s` is not a directory nor a file" % args.input)
