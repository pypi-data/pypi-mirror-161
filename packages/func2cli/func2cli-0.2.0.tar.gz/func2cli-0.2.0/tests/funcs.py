def add_two(a, b):
    """
    Add two numbers together.

    Parameters
    ----------
    a : float
        The first number to add.
    b : float
        The second number to add. But for whatever reason, b has a description
        that stretches over several lines.

    Returns
    -------
    c : float
        The sum of a and b.

    """

    return a + b

def add_with_default(a, b=5):
    """
    Add two numbers with a sensible default.

    Parameters
    ----------
    a : float
        The first number to add.
    b : float
        The second number to add. Defaults to 5.

    Returns
    -------
    c : float
        The sum of a and b.

    """

    return a + b

def add_with_optional_negation(a, b, negate=False):
    """
    Add two numbers with a sensible default.

    Parameters
    ----------
    a : float
        The first number to add.
    b : float
        The second number to add.
    negate : bool
        Whether to negate the sum. Defaults to False.

    Returns
    -------
    c : float
        The sum of a and b, maybe negated.

    """

    c = a + b
    if negate:
        c = -c

    return c

def add_with_negation(a, b, negate):
    """
    Add two numbers with a sensible default.

    Parameters
    ----------
    a : float
        The first number to add.
    b : float
        The second number to add.
    negate : bool
        Whether to negate the sum.

    Returns
    -------
    c : float
        The sum of a and b, maybe negated.

    """

    c = a + b
    if negate:
        c = -c

    return c

def subtract_three(a, b, c):
    """
    Subtract three numbers.

    The usage of this function is a little more complicated, so in addition to
    its short description it has a longer description that is split over not
    just two, but three lines.

    Parameters
    ----------
    a : float
        The number we start with.
    b : float
        The first number we subtract off.
    c : float
        The second number we subtract off.

    Returns
    -------
    d : float
        The result of subtraction, maybe negated.

    """

    return a - b - c
