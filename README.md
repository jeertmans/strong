<p align="center">
<img src="https://raw.githubusercontent.com/jeertmans/strong/main/img/logo.png" width=300></img>
</p>

![](https://img.shields.io/readthedocs/strong) ![](https://img.shields.io/pypi/v/strong) ![](https://img.shields.io/pypi/pyversions/strong)

# Strong - Dynamic type checker for function signatures
Strong embraces the builtin `typing` package by providing dynamic type checking for function signatures.

## Install:

Simply use:

`pip install strong`

## Documentation:

The documentation is hosted [here](https://strong.readthedocs.io/en/latest/).

## Example:

Let's say you have a function taking two inputs, `a` and `b`, and returning one output. In Python, you can use type-hint in order to give clue about the type the parameters should have. Nonetheless, Python will not block inputs with the wrong type.

This package is here to provide tools to make the task of checking input parameters type easy.

```python
>>> from strong.core.decorators import assert_correct_typing

>>> @assert_correct_typing
>>> def f(a: int, b: int) -> int:
>>>     return a + b

>>> x = f(1, 2)  # O.K.

>>> y = f(1, '2')  # K.O.
AssertionError: Function f defined in "<function_file>", line 3
    Argument `b` does not match typing: '2' is not an instance of <class 'int'>
>>> from strong.core.decorators import measure_overhead
>>> import numpy as np

>>> @measure_overhead(assert_correct_typing)
>>> def g(a: int, b: int) -> np.ndarray:
        return np.random.rand(a, b)
    
>>> g(100, 100)
1.0687804670719938  # Ratio between time taken with @assert_correct_typing and without
```
