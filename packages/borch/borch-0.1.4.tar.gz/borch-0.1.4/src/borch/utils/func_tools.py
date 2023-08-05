"""Function tools for python"""
import re
from functools import wraps


def disable_doctests(string):
    """Disable any doctests present in ``string``.

    Notes:
        This should be done by appending the modifier ``# doctest: +SKIP`` at
        the correct position, but this is quite involved. The current fix
        is to replace and occurrence of {>>>,...} with {>>,..} and start
        the docs with an empty >>> to make it render correctly.
    """
    string = re.sub(
        r"(\n\s+)(>>>|\.\.\.)", lambda m: m.group(1) + m.group(2)[:-1], string
    )
    # after replacing to skip doctest add ``>>>`` to render documentation properly
    # add triple > as first line to render correctly in sphinx documentation
    string = re.sub(r"(\n\s+Examples?:\n)(\s+)", r"\1\2>>>\n\2", string)
    return string


def assign_docs(new_cls, old_cls, prefix, skip_doctests=True):
    """Update docs on ``new_cls`` according to how they appear on ``old_cls`` but
    with added information given by ``prefix``."""

    def create_docs(old_docs):
        """Create new docstring with the info contained in ``prefix`` prepended.
        We also optionally replace doctests (the PyTorch doctests seem to be
        unstable)."""
        if old_docs is None:
            return None
        if skip_doctests:
            old_docs = disable_doctests(old_docs)
        return f"{prefix}\n\n{old_docs}"

    new_cls.__init__.__doc__ = create_docs(old_cls.__init__.__doc__)
    new_cls.__doc__ = create_docs(old_cls.__doc__)


def args_to_kwargs(func, *args, **kwargs):
    """
    Takes function and args and kwargs to that function and converts the args
    to kwargs.

    Note: the argument ``self`` is removed.

    Args:
        func: python callable
        *args: non-keyworded variables
        **kwargs: keyworded variables

    Returns:
        dict, with the kwargs to the function

    Example:
        >>> def test_fn(a, b):
        ...     pass
        >>> args_to_kwargs(test_fn, 1, b=2)
        {'b': 2, 'a': 1}
    """
    all_arguments = list(func.__code__.co_varnames)
    if "self" in all_arguments:
        all_arguments.pop(all_arguments.index("self"))
    temp_args = list(args)
    temp_kwargs = kwargs.copy()
    for nn in temp_kwargs.keys():
        all_arguments.pop(all_arguments.index(nn))
    temp_kwargs.update(dict(zip(all_arguments, temp_args)))
    return temp_kwargs


def replace_none_with_argument(argument, func):
    """A decorator which for any function that receives one argument
    (``value``) replace ``value`` with ``argument`` if ``value`` is ``None``."""

    @wraps(func)
    def _new(value=None):
        if value is None:
            value = argument
        return func(value)

    return _new
