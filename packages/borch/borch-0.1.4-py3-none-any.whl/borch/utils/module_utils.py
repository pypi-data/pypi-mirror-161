"""
Common utitility functions to be used with the ppl.Module and its inheritors such as
getting the total number of parameters in a Module or making module static or handling
module attributes.
"""
from copy import deepcopy
from collections import OrderedDict
from numbers import Number
from typing import Iterable, Tuple

from torch import nn

Dims = Tuple[Number, ...]
TupleOfDims = Tuple[Dims, ...]


def total_parameters(module):
    """Return the total number of parameters on a torch.nn.Module (typically
    a neural network).

    Args:
        module (torch.nn.Module): The network for which the number of parameters
          should be calculated.

    Returns:
        int: Number of parameters.

    Examples:
        >>> from torch.nn import Linear, Sequential, Sigmoid
        >>> net = Sequential(
        ...     Linear(3, 4, bias=True), Sigmoid(),
        ...     Linear(4, 5, bias=True), Sigmoid()
        ... )
        >>> total_parameters(net)
        41
    """
    return sum(x.numel() for x in module.parameters())


def _copy_if_possible(val):
    """attempt to copy val if not possible return val"""
    # pylint: disable=bare-except
    try:
        return deepcopy(val)
    except:  # pragma: no cover
        return val


def copy_module_attributes(original, new):
    """Copy attributes from one module to another. Specifically, ensure that
    all tensors in the `_parameters` are assigned the correct class and retain
    attributes.

    Args:
        original: Original module to copy attributes from.
        new: New module to copy attributes to.

    Returns:
        The module `copy` but with all attributes updated according to
        `original`.
    """
    # pylint: disable=protected-access

    # Copy any existing attributes set on the pre-initialised module.
    # This preserves _parameters/_buffers/{pre/post}-hooks or any
    # attribute set on `original`.
    # todo: does deepcopy work for cuda tensors?
    data = deepcopy(original.__dict__)
    for key in list(data):
        val = data[key]
        if isinstance(val, OrderedDict) and hasattr(new, key):
            del data[key]
            getattr(new, key).update(val)
    new.__dict__.update(data)
    return new


def parameters_not_named(module, remove_name):
    """
    Return all paramaters not where the name `remove_name` is part of
    the name yielded by net.named_paramaters.

    Notes:
        If remove_name = 'scale' and the yeilded name is
        linerar.weight.scale.u_tensor then this paramater will not be yeilded
        from this function.
    Args:
        module (torch.nn.Module): the net you want parameters from
        remove_name (str): the name you don't want to in include

    Returns:
        generator where the named params are filtered away.

    """
    for par in yield_not_named(module.named_parameters(), remove_name):
        yield par


def parameters_named(module, include_name):
    """
    Return all parameters where the name name` is part of
    the name yielded by net.named_paramaters.

    Notes:
        If name = 'scale' and the yeilded name is
        linerar.weight.scale.u_tensor then this parameter will be yeilded
        from this function.
    Args:from borch.utils.module_utils import copy_module_attributes
        module (torch.nn.Module): the net you want parameters from
        include_name (str): the name you want to in include

    Returns:
        generator where the named params are filtered away.

    """
    for par in yield_named(module.named_parameters(), include_name):
        yield par


def yield_named(named_parameters, include_name):
    """
    Yield all named parameters whose names do contain the string
    `include_name`.

    Notes:
        If include_name = 'scale' and the yeilded name is
        linerar.weight.scale.u_tensor then this parameter will be yeilded
        from this function.
    Args:
        named_parameters (iterable): parameters you want to filter, should yeild
            name, par
        include_name (str): the name you want to in include

    Returns:
        generator where the named params are filtered away.

    """
    for name, par in named_parameters:
        if include_name in name:
            yield par


def yield_not_named(named_parameters, remove_name):
    """
    Yield all named parameters whose names do not contain the string
    `remove_name`.

    Notes:
        If remove_name = 'scale' and the yeilded name is
        linerar.weight.scale.u_tensor then this paramater will not be yeilded
        from this function.
    Args:
        named_parameters (iterable): parameters you want to filter, should yeild
            name, par
        remove_name (str): the name you don't want to in include

    Yields:
        generator where the named params are filtered away.

    """
    for name, par in named_parameters:
        if remove_name not in name:
            yield par


def get_nested_module(module: nn.Module, index: Iterable[str]) -> nn.Module:
    """Get a (potentially) nested child module from a module.

    Args:
        module: Parent module to index into.
        index: Index to fetch module by.

    Returns:
        An extracted module.

    Example:
        >>> class Net(nn.Module):
        ...     def __init__(self):
        ...         super().__init__()
        ...         self.block = nn.Sequential(nn.Linear(2, 3), nn.Linear(3, 4))
        >>>
        >>> net = Net()
        >>> get_nested_module(net, ("block", "1"))
        Linear(in_features=3, out_features=4, bias=True)
    """
    # pylint: disable=protected-access
    x = module
    for elem in index:
        x = x._modules[elem]
    return x


def get_nested_modules(
    module: nn.Module, indices: Iterable[Iterable[str]]
) -> Tuple[nn.Module]:
    """Get multiple (potentially) nested child modules from a module.

    Args:
        module: Parent module to index into.
        indices: Indices to fetch modules by.

    Returns:
        A tuple of extracted modules.

    Example:
        >>> class Net(nn.Module):
        ...     def __init__(self):
        ...         super().__init__()
        ...         self.block = nn.Sequential(nn.Linear(2, 3), nn.Linear(3, 4))
        >>>
        >>> net = Net()
        >>> modules = get_nested_modules(net, [("block", "0"), ("block", "1")])
        >>> modules[0]
        Linear(in_features=2, out_features=3, bias=True)
        >>> modules[1]
        Linear(in_features=3, out_features=4, bias=True)
    """
    return tuple(get_nested_module(module, i) for i in indices)


def _verify_state_dict_names(module: nn.Module, state_dict: dict):
    expected_parameters = set(name for name, _ in module.named_parameters())
    expected_buffers = set(name for name, _ in module.named_buffers())
    expected = expected_buffers.union(expected_parameters)
    got = set(state_dict.keys())
    msg = ""

    missing = expected.difference(got)
    if missing:
        joined = "', '".join(sorted(missing))
        msg += f"Missing key(s) in state_dict: '{joined}'\n"

    superfluous = got.difference(expected)
    if superfluous:
        joined = "', '".join(sorted(superfluous))
        msg += f"Superfluous key(s) in state_dict: '{joined}'\n"

    if msg:
        raise RuntimeError(msg)


def _prune_state_dict(module: nn.Module, state_dict: dict) -> dict:
    """Prune a state_dict of all entries where the tensors don't match the
    shape of the associated tensors in ``module``."""
    state_dict = dict(state_dict)
    for name, tensor in tuple(state_dict.items()):
        split = name.split(".")
        index, param = split[:-1], split[-1]
        try:
            mod = get_nested_module(module, index)
        except KeyError:
            # we reach here if state_dict contains a module which doesn't
            # exist in `module`
            continue

        mod_tensor = getattr(mod, param, None)
        if mod_tensor is not None and mod_tensor.shape != tensor.shape:
            state_dict.pop(name)

    return state_dict


def load_state_dict(
    module: nn.Module,
    state_dict: dict,
    strict_names: bool = True,
    strict_shapes: bool = True,
):
    """Loads ``state_dict`` into ``module``.

    We can optionally ignore any parameters which are missing or superfluous,
    and/or any parameters which have mismatched shapes.

    Args:
        module: Module to load ``state_dict`` into.
        state_dict: State dict to load.
        strict_names: If ``True``, an error will be raised if there are
          any mismatched names betweeen ``state_dict`` and the module
          contents.
        strict_shapes: If ``True``, an error will be raised if there are
          any mismatched parameter shapes betweeen ``state_dict`` and
          the module contents.

    Example:
        If we have an architecture in which the weight sizes are expected to
        differ on a final layer, we can still forgivingly load a state dict
        as follows:

        >>> from io import BytesIO
        >>> class Network(nn.Sequential):
        ...     def __init__(self, n_out):
        ...         super().__init__()
        ...         self.one = nn.Linear(3, 4)
        ...         self.two = nn.Linear(4, 5)
        ...         self.thr = nn.Linear(5, n_out)
        >>>
        >>> net1 = Network(n_out=10)
        >>> net2 = Network(n_out=20)
        >>> state_dict = net1.state_dict()
        >>> _ = load_state_dict(net2, state_dict, strict_shapes=False)
    """
    if strict_shapes:
        # This is the default PyTorch behaviour
        return module.load_state_dict(state_dict, strict=strict_names)

    state_dict = state_dict.copy()
    if strict_names:
        _verify_state_dict_names(module, state_dict)
    state_dict = _prune_state_dict(module, state_dict)
    return module.load_state_dict(state_dict, strict=False)
