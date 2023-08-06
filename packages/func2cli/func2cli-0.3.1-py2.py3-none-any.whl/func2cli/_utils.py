import builtins
import functools
import inspect

from argparse import BooleanOptionalAction

def default_parse_func(func):
    """
    Parse a function and its docstring, and return data for argument parsing.

    The default parse assumes that the docstring has a single-line summary of
    func, followed by a blank line, and then a series of parameter descriptions
    following ten dashes (as below). The parameter descriptions should consist
    of the parameter name and type, separated by a colon, on one line, followed
    by an indented description of the parameter. The parameter list should be
    separated from the rest of the docstring by a blank line.

    Parameters
    ----------
    func : function
        The function to be parsed.

    Returns
    -------
    name : str
        A sanitized version of func.__name__.
    description : str
        A description of the behavior of func.
    params : list of dict
        A list of keyword argument dictionaries that can be passed to successive
        calls to add_argument.

    """

    name = func.__name__.replace('_', '-')
    docstring = func.__doc__

    start = docstring.index('\n') + 1
    end = docstring.index('\n\n')
    description = docstring[start:end].strip()

    header = 'Parameters\n    ----------\n'
    docstring = docstring[(docstring.index(header) + len(header)):]
    docstring = docstring[:docstring.index('\n\n')]

    defaults = _get_defaults(func)
    params = _get_params(docstring, defaults)

    return name, description, params

def _get_defaults(func):
    defaults = {}
    for k, v in inspect.signature(func).parameters.items():
        if v.default is not inspect.Parameter.empty:
            defaults[k] = v.default

    return defaults

def _get_params(docstring, defaults):
    params = []
    for line in [s[4:] for s in docstring.split('\n')]:
        if not line.startswith('    '):
            param_name, type_name = line.split(' : ')
            default = defaults.get(param_name, None)
            prefix = '--' if param_name in defaults else ''

            if prefix:
                param_name = param_name.replace('_', '-')

            params.append({
                'param_name' : prefix + param_name,
                'metavar' : param_name.replace('_', '-'),
                'type' : _get_type(type_name),
                'default' : default
            })

        else:
            params[-1].setdefault('help', []).append(line.strip())

    for param in params:
        param['help'] = ' '.join(param['help']).replace('_', '-')

    return params

def _get_type(type_name):
    if type_name.startswith('list'):
        type_name = type_name.split(' of ')[-1]
        cast = _get_type(type_name)

        return functools.partial(_parse_list, cast=cast)

    if type_name == 'bool':
        return _parse_bool

    return getattr(builtins, type_name)

def _parse_bool(s):
    return {'True' : True, 'False' : False}[s]

def _parse_list(s, cast):
    return [cast(v) for v in s.split(',')]
