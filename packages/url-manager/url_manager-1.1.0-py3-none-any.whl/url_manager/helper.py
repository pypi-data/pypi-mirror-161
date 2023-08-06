import functools


def compose(*functions):
    """
    Compose a list of functions into a single function.
    """
    return functools.reduce(lambda f, g: lambda x: g(f(x)), functions)
