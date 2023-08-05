"""A ``Graph`` merges Module and a tensor

The forward needs to return a single tensor, the Graph can be used as a tensor
where it will have the value the last returned value from the forward.
"""
from numbers import Number
import functools
from typing import Tuple
from numpy import ndarray

import torch
from torch.nn.parameter import Parameter
from torch import Tensor

from borch.utils.func_tools import disable_doctests
import borch.module as module

TENSOR_ATTR = "_tensor"


def as_tensor(val, promote_number=True):
    """Convert val to a ``torch.Tensor`` if possible

    Examples:
        >>> as_tensor(1.)
        tensor(1.)
        >>> as_tensor('hello')
        'hello'
    """
    if promote_number and isinstance(val, Number):
        val = torch.tensor(val, dtype=torch.float32)  # pylint: disable=not-callable
    if isinstance(val, list) and isinstance(val[0], (torch.Tensor, Graph)):
        return [as_tensor(x) for x in val]
    if isinstance(val, (list, ndarray)):
        val = torch.tensor(val, dtype=torch.float32)  # pylint: disable=not-callable
    if isinstance(val, Graph):
        return val.tensor
    return val


def empty_graph(mod):
    """Remove the saved tensor value from `Graph`s

    Examples:
        >>> import borch
        >>> net = borch.nn.Linear(1,2)
        >>> _ = net.apply(empty_graph)
    """
    if isinstance(mod, Graph):
        mod.tensor = torch.empty(0)


def _update_graph_tensor(
    self, inpt: Tuple[()], output: Tensor
):  # pylint: disable=unused-argument, protected-access
    self._tensor = as_tensor(output)
    return self._tensor


class Graph(module.Module):
    """A ``borch.Module`` that can act as a tensor.

    A graph``s forward takes no arguments and returns a single tensor.
    This tensor is stored with the graph and the graph iteself can act
    as the tensor.

    Note: This is a base class and is intended to be inherited from and not be
    used directly.

    Examples:
        >>> import torch
        >>> class Exp(Graph):
        ...     'Apply the exp transform'
        ...     def __init__(self, param):
        ...         super().__init__()
        ...         self.register_param_or_buffer("param", param)
        ...     def forward(self):
        ...         return torch.exp(self.param)

        >>> exp = Exp(torch.nn.Parameter(torch.zeros(1)))
        >>> exp*1
        tensor([1.], grad_fn=<MulBackward0>)
        >>> list(exp.parameters())
        [Parameter containing:
        tensor([0.], requires_grad=True)]
    """

    # pylint: disable=abstract-method

    def __init__(self, posterior=None):
        # pylint: disable=not-callable
        super().__init__(posterior=posterior)
        self.register_buffer(
            TENSOR_ATTR,
            torch.empty(0),
            persistent=True,
        )
        self.register_forward_hook(_update_graph_tensor)

    def has_been_run(self):
        """Check if the graph has been executed such there is a .tensor value"""
        return self._tensor.nelement() != 0

    @property
    def tensor(self):
        """Access the value of the last forward of the graph"""
        if not self.has_been_run():
            self()
        return self._tensor

    @tensor.setter
    def tensor(self, x):
        self._tensor = x

    def register_param_or_buffer(self, name, val):
        """Register val as a parameter if it is a Parameter as a tensor if it
        is or can be cast to a tensor and setattr as a fallback"""
        if isinstance(val, (Number, list, ndarray)):
            val = torch.tensor(val, dtype=torch.float32)  # pylint: disable=not-callable
        if isinstance(val, Parameter):
            self.register_parameter(name, val)
        elif isinstance(val, Tensor):
            self.register_buffer(name, val, persistent=True)
        else:
            setattr(self, name, val)

    def __repr__(self):
        return f"{self.__class__.__name__}: \n {repr(self.tensor)}"

    @classmethod
    def __torch_function__(
        cls, func, types, args=(), kwargs=None
    ):  # pylint: disable=unused-argument
        if kwargs is None:
            kwargs = {}
        with torch._C.DisableTorchFunction():  # pylint: disable=protected-access
            args = [as_tensor(arg, promote_number=False) for arg in args]
            kwargs = {
                key: as_tensor(val, promote_number=False) for key, val in kwargs.items()
            }
            return func(*args, **kwargs)


def _overload_tensor_method(cls, method):
    @functools.wraps(getattr(torch.Tensor, method))
    def _fn(self, *args):
        return getattr(torch.Tensor, method)(self.tensor, *args)

    if _fn.__doc__:
        _fn.__doc__ = disable_doctests(_fn.__doc__)
    setattr(cls, method, _fn)


def _overload_tensor_property(cls, prop):
    @functools.wraps(getattr(torch.Tensor, prop))
    def _fn(self):
        return getattr(self.tensor, prop)

    if _fn.__doc__:
        _fn.__doc__ = disable_doctests(_fn.__doc__)
    setattr(cls, prop, property(_fn))


def _overloadable_tensor_methods():
    overloadable = []
    for key in dir(torch.Tensor):
        if callable(getattr(torch.Tensor, key)):
            overloadable.append(key)
    return set(overloadable)


def _overloadable_tensor_propperties():
    overloadable = []
    for key in dir(torch.Tensor):
        if not callable(getattr(torch.Tensor, key)) and not key.startswith("_"):
            overloadable.append(key)
    return set(overloadable)


for _op in _overloadable_tensor_methods() - set(dir(Graph)):
    _overload_tensor_method(Graph, _op)

# They break torch.jit.trace
UNSUPORTED = {"imag", "real"}
for _op in _overloadable_tensor_propperties() - set(dir(Graph)) - UNSUPORTED:
    _overload_tensor_property(Graph, _op)
