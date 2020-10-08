from strong.core.signature import (
    check_obj_typing
)
from typing import List, Tuple, Optional, Mapping, Union, Set, Any

from unittest import TestCase


class SubInt(int):
    pass


class Foo:
    pass


class TestDecorators(TestCase):
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
        ]

        for i, arg in enumerate(args):
            with self.subTest(i=i):
                got = check_obj_typing(arg[1], arg[0])
                self.assertFalse(got)
