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
from pysign import assert_correct_typing

@assert_correct_typing
def f(a: int, b: int) -> int:
    return a + b
  
x = f(1, 2)  # O.K.

y = f(1, '2')  # K.O.
>>> ...
>>> AssertionError: Return value does not match typing: '2' is not an instance of <class 'int'>
```
