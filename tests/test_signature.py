from strong.core.signature import (
    get_function_parameters,
    check_obj_typing,
)
from functions import (
    f_mul_int_typed,
    f_mul_int_missing_one,
    f_mul_int_missing_two,
    f_mul_int_missing_all,
    f_mul_int_typed_kwd,
    f_mul_int_typed_from_string,
)
from objects import Foo, SubInt
from typing import List, Tuple, Optional, Mapping, Union, Set, Any, Callable
import inspect

from unittest import TestCase


def ok_get_function_signature(f):
    sign = inspect.signature(f)
    return sign.parameters, sign.return_annotation


class TestDecorators(TestCase):
    def test_get_function_signature(self):

        my_func = get_function_parameters
        ok_func = ok_get_function_signature

        # 1. Check that output is consistent

        args = [
            f_mul_int_typed,
            f_mul_int_missing_one,
            f_mul_int_missing_two,
            f_mul_int_missing_all,
            f_mul_int_typed_kwd,
            f_mul_int_typed_from_string,
        ]

        for i, arg in enumerate(args):
            with self.subTest(i=i):
                got = my_func(arg)
                expected = ok_func(arg)
                self.assertEqual(got, expected)

    def test_check_obj_typing(self):

        # 1. Check for correct typing

        args = [
            (4, int),
            (4, Any),
            (SubInt(), int),
            (Foo(), Foo),
            (4, Union[int, float]),
            (4, Optional[int]),
            ([4, 5], List[int]),
            ([4, None], List[Optional[int]]),
            ([SubInt(4), 4, 3.0, Foo()], List[Union[int, float, Foo]]),
            ({"k": 1, 2: 3, "a": 33}, Mapping[Union[str, int], int]),
            ((1, "b", 3.0), Tuple[int, str, float]),
            ({1, 2, 3}, Set[int]),
            (f_mul_int_typed, Callable[[int, int], float])
        ]

        for i, arg in enumerate(args):
            with self.subTest(i=i):
                got = check_obj_typing(arg[1], arg[0])
                self.assertTrue(got)

        # 2. Check for incorrect typing

        args = [
            (4, SubInt),
            (SubInt(), float),
            (Foo(), int),
            (4, Union[float]),
            (4, Optional[float]),
            ([4, 5], Set[int]),
            ([4, None], List[int]),
            ([SubInt(4), 4, 3.0, Foo()], List[Tuple[int, float, Foo]]),
            ({"k": 1, 2: 3, "a": 33}, Mapping[Union[str], int]),
            ((1, "b", 3.0), Tuple[int, str, float, str]),
            ({1, 2, 3}, Set[float]),
            (f_mul_int_typed, Callable[[int, int], int])
        ]

        for i, arg in enumerate(args):
            with self.subTest(i=i):
                got = check_obj_typing(arg[1], arg[0])
                self.assertFalse(got)
