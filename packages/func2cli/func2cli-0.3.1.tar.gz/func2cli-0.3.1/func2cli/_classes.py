import argparse

from ._utils import default_parse_func

class FunctionParser:
    """
    Parser class for modules that perform one out of a list of functions.

    FunctionParser should be used when a script is intended to execute one out
    of a list of one or more functions, and the command line arguments might
    change depending on which function is selected by the user. FunctionParser
    reads the docstrings for the functions that can be selected, sets up
    argument parsing that automatically matches the call signatures of those
    functions, and adds descriptions to each argument from the docstrings.

    """

    def __init__(self, funcs, parse_func=default_parse_func):
        """
        Initialize a FunctionParser.

        Parameters
        ----------
        funcs : function or list of functions
            A single function or a list of functions. If a single function, the
            command line interface will accept arguments to that function
            directly, whereas if a list of functions is passed, the CLI will
            first take one of their names as a positional argument. All
            functions should have a docstring readable by parse_func.
        parse_func : function, optional
            A function to parse a function and extract relevant information from
            its docstring. It should match the signature of default_parse_func.
            Defaults to using default_parse_func, which parses functions with
            docstrings similar to this one.

        """

        if callable(funcs):
            _, description, params = parse_func(funcs)
            self.parser = argparse.ArgumentParser(
                description=description,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter
            )

            self.parser.set_defaults(func=funcs)
            _add_params_to_parser(params, self.parser)

        else:
            self.parser = argparse.ArgumentParser()
            adder = self.parser.add_subparsers()

            for func in funcs:
                name, description, params = parse_func(func)
                subparser = adder.add_parser(
                    name, help=description, description=description,
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter
                )

                subparser.set_defaults(func=func)
                _add_params_to_parser(params, subparser)

    def run(self, args=None):
        """Runs the selected function with the passed arguments."""

        kwargs = vars(self.parser.parse_args(args))
        func = kwargs.pop('func')

        return func(**kwargs)

def _add_params_to_parser(params, parser):
    for param in params:
        param_name = param.pop('param_name')
        parser.add_argument(param_name, **param)
