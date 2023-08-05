from func2cli import FunctionParser
from tests.funcs import (
    add_two,
    add_with_default,
    add_with_optional_negation,
    add_with_negation,
    subtract_three
)

def test_required_bool():
    parser = FunctionParser([add_with_negation])

    assert parser.run(['add-with-negation', '4', '6', 'False']) == 10
    assert parser.run(['add-with-negation', '4', '6', 'True']) == -10

def test_multiple():
    parser = FunctionParser([add_two, subtract_three])

    assert parser.run(['add-two', '2', '3']) == 5
    assert parser.run(['subtract-three', '10', '7', '5']) == -2

def test_optional():
    parser = FunctionParser([add_with_default])

    assert parser.run(['add-with-default', '1']) == 6
    assert parser.run(['add-with-default', '1', '--b', '-2']) == -1

def test_optional_bool():
    parser = FunctionParser([add_with_optional_negation])

    assert parser.run(['add-with-optional-negation', '4', '6']) == 10
    assert parser.run([
        'add-with-optional-negation',
        '4', '6',
        '--negate', 'True']
    ) == -10

def test_single():
    parser = FunctionParser(add_with_negation)

    assert parser.run(['4', '6', 'False']) == 10
    assert parser.run(['4', '6', 'True']) == -10
