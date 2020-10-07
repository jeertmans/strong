from pysign.decorators import *

from unittest import TestCase


def f_mul_int(a: int, b: int) -> float:
    return a * b * 0.5


class TestDecorators(TestCase):

    def test_assert_correct_typing(self):
        my_func = assert_correct_typing(f_mul_int)
