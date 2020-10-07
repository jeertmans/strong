<p align="center">
<img src="https://raw.githubusercontent.com/jeertmans/pysign/main/img/logo.png" width=300></img>
</p>
<p align="center">
<a href="http://www.freepik.com">Designed by Freepik</a>
</p>

# PySign - from type-hint to real typing
PySign is a small package written in pure Python and aiming to provide easy-to-use tools to validate the type of parameters and output of a given function.

## Example:

Let's say you have a function taking two inputs, `a` and `b`, and returning one output. In Python, you can use type-hint in order to give clue about the type the parameters should have. Nonetheless, Python will not block inputs with the wrong type.

This package is here to provide tools to make the task of checking input parameters type easy.

```python
[1] from pysign.core.decorators import assert_correct_typing
[2] 
[3] @assert_correct_typing
[4] def f(a: int, b: int) -> int:
[5]     return a + b
[6]  
[7] x = f(1, 2)  # O.K.
[8]
[9] y = f(1, '2')  # K.O.
>>> AssertionError: Function f defined in "<function_file>", line 3
>>>     Argument `b` does not match typing: '2' is not an instance of <class 'int'>
[10] from pysign.core.decorators import measure_overhead
[11] import numpy as np
[12]
[13] @measure_overhead(assert_correct_typing)
[14] def g(a: int, b: int) -> np.ndarray:
[15]    return np.random.rand(a, b)
[16]
[17] g(100, 100)
>>> 1.0687804670719938  # Ratio between time taken with @assert_correct_typing and without
```
