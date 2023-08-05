`func2cli` is a wrapper around the standard Python `argparse` library that intelligently passes arguments from the command line to one or more Python functions. `func2cli` reads the docstrings of those functions and extracts relevant information that is then passed to calls of the `add_argument` method of `argparse` parsers.

`func2cli` can be installed with
```
pip install func2cli
```

The example script below uses `func2cli` to pass command line arguments to one of two simple functions.
```python
# script.py

from func2cli import FunctionParser

def add_three(a, b, c=7):
    """
    Add three numbers together.

    Parameters
    ----------
    a : float
        The first number to add.
    b : float
        The second number to add.
    c : float
        The third number to add.

    Returns
    -------
    d : float
        The sum of a, b, and c.

    """

    return a + b + c

def modify_string(s, reverse=False):
    """
    Make a string upper case, and maybe reverse it.

    Parameters
    ----------
    s : str
        The original string.
    reverse : bool
        Whether to reverse the string.

    Returns
    -------
    output : str
        The modified string.

    """

    output = s.upper()
    if reverse:
        output = output[::-1]

    return output

if __name__ == '__main__':
    parser = FunctionParser([add_three, modify_string])
    output = parser.run()
    print(output)
```
Usage information is automatically available at the command line.
```console
$ python script.py -h
usage: script.py [-h] {add-three,modify-string} ...

positional arguments:
  {add-three,modify-string}
    add-three           Add three numbers together.
    modify-string       Make a string upper case, and maybe reverse it.

options:
  -h, --help            show this help message and exit
```
`script.py` has two allowed positional arguments, one for each of the functions passed to the `FunctionParser`. Moreover, usage information for individual positional arguments can also be displayed.
```console
$ python script.py add-three -h
usage: script.py add-three [-h] [--c c] a b

positional arguments:
  a           The first number to add.
  b           The second number to add.

options:
  -h, --help  show this help message and exit
  --c c       The third number to add. (default: 7)
```
`func2cli` automatically treats parameters with default values as optional command line arguments.
```console
$ python script.py add-three 2 4
13.0
$ python script.py add-three 2 4 --c -8
-2.0
```
The `FunctionParser` knows what types are permissible for each argument. For example, the arguments to `add-three` should all be floats, and so an invalid argument passed at the command line raises an error.
```console
$ python script.py add-three 1 foo
usage: script.py add-three [-h] [--c c] a b
script.py add-three: error: argument b: invalid float value: 'foo'
```
Boolean arguments should be passed as the strings `True` and `False`. This convention breaks with traditional `argparse` idioms, but makes the resulting command line statements more similar to their corresponding Python function calls.
```console
$ python script.py modify-string -h
usage: script.py modify-string [-h] [--reverse reverse] s

positional arguments:
  s                  The original string.

options:
  -h, --help         show this help message and exit
  --reverse reverse  Whether to reverse the string. (default: False)
$ python script.py modify-string hello --reverse True
OLLEH
```
By default, `func2cli` assumes that function docstrings look like the ones shown in `script.py` above. However, `func2cli` supports arbitrary docstring conventions by allowing the user to pass a custom `parse_func` argument to `FunctionParser`.
