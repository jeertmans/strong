

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


def f_mul_int_typed_kwd(a: int, b: int = 0) -> float:
    return f_mul(a, b)


__f_mul_int_typed_from_string__ = None
__f_mul_int_typed_code__ = """def __f_mul_int_typed_from_string__(
a: int, b:int) -> float:
    return f_mul(a, b)
"""

exec(__f_mul_int_typed_code__)

f_mul_int_typed_from_string = __f_mul_int_typed_from_string__
