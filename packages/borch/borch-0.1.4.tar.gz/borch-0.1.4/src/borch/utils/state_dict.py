"""
Functionality to operate on state_dicts
"""
from io import BytesIO
import pickle as pkl
import random


def add_state_dict_to_state(module, state):
    """Save the current state of a module"""
    state = list(state)
    state.append(copy_state_dict(module.state_dict()))
    return state


def sample_state(module, state, idx=None):
    """Restore one of the saved states"""
    if idx is None:
        idx = random.randint(0, len(state) - 1)
    module.load_state_dict(state[idx])


def state_dict_to_device_(state_dict, device):
    """
    Send all values in a statedict to a given device. When encounters values that
    contain parameters, it will loop through those parameters and put them on the device
    as well. Note if the parameters have further sub_parameters we are not recursing
    into them.

    Args:
        state_dict: A state_dict from an borch.borch.nn.module

    Returns:
        state_dict: the modified input state_dict

    Examples:
        >>> import torch
        >>> from borch import nn
        >>> net = nn.Sequential(nn.Conv2d(3,10, 3), nn.Conv2d(10, 11, 3))
        >>> state_dict = net.state_dict()
        >>> new_state_dict = saveable_state_dict(state_dict)
    """

    for k, val in state_dict.items():
        state_dict[k] = val.to(device)

    return state_dict


def copy_state_dict(state_dict):
    """
    Takes a copy of a state_dict by serializing and deserializing it using pickle.

    Args:
        state_dict: state_dict to copy

    Returns:
        new_state_dict: copy of state_dict

    """
    with BytesIO() as bytes_io:
        pkl.dump(state_dict, bytes_io)
        bytes_io.seek(0)
        new_state_dict = pkl.load(bytes_io)
    return new_state_dict


def saveable_state_dict(state_dict):
    """
    Copies a statedict and puts it on cpu and unobserve all variables in it

    Args:
        state_dict: state_dict that we to save

    Returns:
        state_dict: the modified input state_dict
    """

    new_state_dict = copy_state_dict(state_dict)
    new_state_dict = state_dict_to_device_(new_state_dict, "cpu")
    return new_state_dict
