from pysign.decorators import *

from unittest import TestCase


def f_mul(a, b):
    return a * b * 0.5


def f_mul_int_typed(a: int, b: int) -> float:
    return f_mul(a, b)


def f_mul_int_missing_one(a: int, b) -> float:
    return f_mul(a, b)


def f_mul_int_missing_two(a, b) -> float:
    return f_mul(a, b)


def f_mul_int_missing_all(a, b):
    return f_mul(a, b)


class TestDecorators(TestCase):
    def test_assert_correct_typing(self):

        f = assert_correct_typing(f_mul_int_typed)
        f_1 = assert_correct_typing(f_mul_int_missing_one)
        f_2 = assert_correct_typing(f_mul_int_missing_two)
        f_a = assert_correct_typing(f_mul_int_missing_all)

        # 1. Check with correct typing

        a, b = 1, 2

        f(a, b)
        f_1(a, b)
        f_2(a, b)
        f_a(a, b)

        # 2. Check with incorrect typing
        assert_msg = "AssertionError should have been raised"
        no_assert_msg = "Not error should have been raised"

        a, b = 1, 0.5

        try:
            f(a, b)
            error = None
        except AssertionError as e:
            error = e
        assert isinstance(error, AssertionError), assert_msg

        try:
            f_1(a, b)
            error = None
        except AssertionError as e:
            error = e
        self.assertEqual(error, None, msg=no_assert_msg)

        try:
            f_2(a, b)
            error = None
        except AssertionError as e:
            error = e
        self.assertEqual(error, None, msg=no_assert_msg)

        try:
            f_a(a, b)
            error = None
        except AssertionError as e:
            error = e
        self.assertEqual(error, None, msg=no_assert_msg)

        a, b = 1, 1j

        try:
            f(a, b)
            error = None
        except AssertionError as e:
            error = e
        assert isinstance(error, AssertionError), assert_msg

        try:
            f_1(a, b)
            error = None
        except AssertionError as e:
            error = e
        assert isinstance(error, AssertionError), assert_msg

        try:
            f_2(a, b)
            error = None
        except AssertionError as e:
            error = e
        assert isinstance(error, AssertionError), assert_msg

        try:
            f_a(a, b)
            error = None
        except AssertionError as e:
            error = e
        self.assertEqual(error, None, msg=no_assert_msg)
