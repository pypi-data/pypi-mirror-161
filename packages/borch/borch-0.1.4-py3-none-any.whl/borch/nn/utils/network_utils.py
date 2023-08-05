"""
Network Utils
=============

Common utilities to use on `torch.nn.Module` and it's inheritors. This includes
things such as getting the total number of parameters in a neural network, and
calculating the dimensionality of an input image after a number of
convolutional layers.
"""

from numbers import Number
from typing import Tuple, Union
import pickle as pkl

from torch import nn

from borch.utils.state_dict import saveable_state_dict
from borch.utils.module_utils import load_state_dict

Dims = Tuple[Number, ...]
TupleOfDims = Tuple[Dims, ...]


def static(module):
    """Make all the paramaters of a module and its children static.

    This involves calling the ``detach_`` inplace operation on all
    parameters and putting the module in ``eval`` mode.

    Args:
        module (torch.nn.Module): Module to make static.

    Returns:
        (torch.nn.Module) a static net

    Notes:
        This is an inplace operation!!!!

    Examples:
        >>> net = nn.Sequential(nn.Linear(4, 4), nn.ReLU(), nn.Linear(4, 10))
        >>> static_net = static(net)
    """
    for par in module.parameters():
        par.detach_()
    module.eval()

    return module


def split_sequential_into_two(net, index):
    """
    Splits a sequential into two sequentials according to the secified index.

    Args:
        net (Sequential): the sequential object to split
        index (int): where to split the network. ex. -1 would result in the
        last layer of net as its own sequential and the all the other layes
        in the first sequential

    Returns:
        Sequential, Sequential: two Sequential modules

    """
    if not isinstance(net, nn.Sequential):
        raise ValueError("net needs to be a sequential")
    if not isinstance(index, int):
        raise ValueError("index should be an int")

    modules = net._modules.values()  # pylint: disable=protected-access
    if index < 0:
        index = len(modules) + index - 1

    seq1, seq2 = [], []
    for ii, module in enumerate(modules):
        if ii <= index:
            seq1.append(module)
        else:
            seq2.append(module)
    return type(net)(*seq1), type(net)(*seq2)


def calculate_post_convolution_dims(
    dim: Dims, kernel_sizes: Union[Dims, TupleOfDims], strides: Union[Dims, TupleOfDims]
) -> tuple:
    r"""Calculate the spatial dimensionality of features after a number of
    convolutional layers.

    For each spatial dimension ..math::`d` and each layer ..math::`l`, this is:

    .. math::
        x_{d,l+1} =
        \left\lfloor
          \frac{x_{d,l} - \left\lfloor k_{d,l} \right\rfloor_e}{s_{d,l}}
        \right\rfloor

    where ..math::`x` is input dimension, ..math::`k` is kernel size,
    ..math::`s` is stride, and ..math::`\left\lfloor x \right\rfloor_e` is the
    floor to the nearest even number.

    Args:
        dim: Initial dimension of the incoming image/data.
        kernel_sizes: Kernel sizes at each convolutional layer. Each element in
          kernel_sizes must be either an `int` or a tuple matching the
          dimensionality of `dim`.
        strides: Stride sizes at each convolutional layer. Each element in
          strides must be either an `int` or a tuple matching the
          dimensionality of `dim`.

    Todo:
        * Update all type definitions to be tuples or lists.

    Examples:
        >>> # A typical use case for a 28x28 pixel input (e.g. MNIST) with
        >>> # equal kernel sizes (strides) of 9x9 (1x1) for layer 1 and
        >>> # 9x9 (2x2) for layer 2:
        >>> calculate_post_convolution_dims((28, 28), [9, 9], [1, 2])
        (6, 6)

        >>> # It works for arbitrary dimensionality, an example for a 3D input
        >>> # with 1 convolutional layer with kernel size 9x7x9 and a stride
        >>> # of 1x2x3:
        >>> calculate_post_convolution_dims(
        ...     (28, 28, 32), [(9, 7, 5)], [(1, 2, 3)]
        ... )
        (20, 11, 9)
    """

    if not kernel_sizes:  # base-case
        return dim

    if len(kernel_sizes) != len(strides):
        raise ValueError(
            f"Number of kernel sizes ({len(kernel_sizes)}) must"
            f" match number of strides ({len(strides)})"
        )

    kernel_size = _coerce_type(kernel_sizes[0], "kernel size", dim)
    stride = _coerce_type(strides[0], "stride", dim)

    if len(dim) != len(kernel_size) or len(dim) != len(stride):
        raise ValueError(
            f"One of: dimension of dim ({len(dim)}), dimension of kernel size"
            f" ({len(kernel_size)}) or dimension of stride ({len(stride)})"
            " did not match."
        )

    new_dim = tuple(
        (d - (2 * (k // 2))) // s for d, k, s in zip(dim, kernel_size, stride)
    )

    return calculate_post_convolution_dims(new_dim, kernel_sizes[1:], strides[1:])


def _coerce_type(obj, name, dim):
    if isinstance(obj, int):
        return tuple(obj for _ in dim)
    if not isinstance(obj, tuple) or isinstance(obj, list):
        raise ValueError(f"{name} {obj} is not a tuple, list or int.")
    return obj


def save_net_state(net, path):
    """
    Extracts the state of a network, prepares it for saving and saves it at the given
    path

    Args:
        net: The network, of which state dict we want to save
        path: The path at which we want to save the statedict

    Returns:
        None

    Examples:
        >>>
        >> from borch import nn
        >> net = nn.Sequential(nn.Conv2d(3, 10, 3), nn.Conv2d(10, 10, 3))
        >> path = "the/path/we/save/path.pth"
        >> save_net_state(net, path)
    """
    state_dict = net.state_dict()
    state_dict = saveable_state_dict(state_dict)
    with open(path, "wb") as f:
        pkl.dump(state_dict, f)


def load_net_state(
    net,
    path,
    ignore_missing_names=False,
    ignore_unexpected_names=True,
    strict_shapes=True,
):
    """
    Load the state from a path and load it to the network

    Args:
        net: The initialized network we want to load out statedict into
        path: The path at which we have saved the network state dict
        strict: If set to True it will throw an error if the state dict of net and the
            state dict at path does not have exactly mathcing keys. If set to false it
            will load the values that are shared between the two state dicts

    Returns:
        None

    Examples:
        >>>
        >> from borch import nn
        >> net = nn.Sequential(nn.Conv2d(3, 10, 3), nn.Conv2d(10, 10, 3))
        >> path = "path/to/saved/state_dict.pth"
        >> save_net_state(net, path)
    """
    with open(path, "rb") as f:
        state_dict = pkl.load(f)

    if ignore_unexpected_names:
        for extra_key in set(state_dict.keys()) - set(net.state_dict().keys()):
            state_dict.pop(extra_key)

    strict_names = not ignore_missing_names

    load_state_dict(
        net, state_dict, strict_shapes=strict_shapes, strict_names=strict_names
    )
    return net
