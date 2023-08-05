"""
Utility functions for manipulation and introspection of ``torch.tensor``s.
"""
from numbers import Number
import random
import numpy as np
import torch


def is_numeric(val):
    """Check if it a numeric value"""
    if isinstance(val, bool):
        return False
    if isinstance(val, (Number, torch.Tensor)):
        return True
    return False


def get_device():
    """Get current device, cuda if available else CPU"""
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def seed(seed):  # pylint: disable=redefined-outer-name
    """Seed the random number generator.

    Args:
        seed (int): Seed number to use.

    """
    torch.manual_seed(seed)
    if torch.cuda.is_available():  # pragma: no cover
        torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)


def grads_to_none(params):
    """
    Set the gardients to None for all params
    Args:
        params (iterable): iterable with ``torch.Tensors``

    Notes:
        Warning, this is an in place operation
    """
    for par in params:
        par.grad = None


def is_optimizable_leaf_tensor(tensor):
    """
    Checks if the tensor is a leaf node and requires grad
    Args:
        tensor (torch.tensor): the tensor that ig going to be checked

    Returns:
        Boolean, True if the tensor is a leaf node and requires grad

    Examples:
        >>> var = torch.randn(3, requires_grad=True)
        >>> is_optimizable_leaf_tensor(var)
        True

    """
    if tensor.is_leaf and tensor.requires_grad:
        return True
    return False


def detach_tensor_dict(tensor_dict):
    """Returns a new dictionary where ``.detach()`` have been called on all the
    value elements of the dict.

    Args:
      tensor_dict: Dictionary where the values are torch.tensor's

    Returns:
      Dictionary

    Example:
        >>> import torch
        >>> tensor_dict = {str(ii): torch.randn(1, requires_grad=True)
        ...     for ii in range(3)}
        >>> new_tensor_dict = detach_tensor_dict(tensor_dict)
        >>> tensor_dict['1'].requires_grad
        True
        >>> new_tensor_dict['1'].requires_grad
        False
    """
    return {key: val.detach() for key, val in tensor_dict.items()}


def detach_copy_tensors(tensors):
    """Returns a new list where ``.detach().clone()`` have been called on all
        the elements of the list.

    Args:
      tensors: List where the elements are torch.tensor's

    Returns:
      list

    Example:
        >>> import torch
        >>> x = torch.randn(10, requires_grad = True)
        >>> x.requires_grad
        True
        >>> new_x = new_tensor_list = detach_copy_tensors([x])[0]
        >>> new_x.requires_grad
        False
    """
    return [val.detach().clone() for val in tensors]


def update_tensor_data(tensor_list, data_list):
    """Updates the data of the tensor's in the tensor list with values of the
    data_list. Where element one of the tensor_list is updated with elemnt one
    of the data_list etc.

    Args:
      tensor_list: List with ``torch.tenor``'s
      data_list: List with ``torch.tenor``'s

    Returns:
      None

    Examples:
        >>> import torch
        >>> tensor_list = [torch.randn(1, requires_grad=True)]
        >>> data_list = [torch.tensor([1.2])]
        >>> update_tensor_data(tensor_list, data_list)
        >>> tensor_list[0].data
        tensor([1.2000])
        >>> data_list[0]
        tensor([1.2000])
    """
    for tensor, data in zip(tensor_list, data_list):
        tensor.data = data.data


def dict_values_to_tensor(dictionary):
    """
    Converts all values in the dictionary that is an instance of
    ``numbers.Number`` to a tensor. If some of the values are allready a
    ``torch.tensor`` then all of the new tensors will be moved to the same device.
    In the case there are several ``torch.tensors`` on different devices, then it
    will be placed on a random device.

    Args:
        dictionary (dict): a dictionary with values to convert to tensors

    Returns:
        dictionary where all values that inherited from ``numbers.Number`` are
        converted to torch.tensors.

    Examples:
        >>> import torch
        >>> temp = {'a': 1., 'b': torch.tensor(1.), 'c': 2}
        >>> dict_values_to_tensor(temp)
        {'a': tensor(1.), 'b': tensor(1.), 'c': tensor(2.)}
    """
    # pylint: disable=not-callable
    temp = dictionary.copy()
    tensors_in_dict = [val for val in temp.values() if isinstance(val, torch.Tensor)]
    for key, val in temp.items():
        if isinstance(val, Number):
            new_tensor = torch.tensor(float(val))
            if tensors_in_dict:
                new_tensor = new_tensor.type_as(tensors_in_dict[0])
            temp[key] = new_tensor
    return temp


def one_hot(labels: torch.LongTensor, n_classes: int) -> torch.Tensor:
    r"""Given a tensor of class encodings ..math::``X \in \{0, ..., C-1\}^N``
    where ..math::``C`` is the number of classes, and ..math::``N`` is the number
    of datapoints, convert it to a 'one-hot' tensor
    ..math::``Y \in \{0, 1\}^{N \times C}`` where
    ..math::``Y_{i,j} = \delta_{X_i,j-1}``.

    Args:
        labels: A tensor of class encodings.
        n_classes: Total number of classes encoded (e.g. 10 for MNIST).

    Returns:
        A one-hot encoded tensor of shape ``[len(labels), n_classes]``.

    Example:
        >>> a = torch.LongTensor([0, 1, 1, 3])
        >>> one_hot(a, n_classes=5)
        tensor([[1., 0., 0., 0., 0.],
                [0., 1., 0., 0., 0.],
                [0., 1., 0., 0., 0.],
                [0., 0., 0., 1., 0.]])

    """
    zeros = torch.zeros(labels.size(0), n_classes, device=labels.device)
    return zeros.scatter_(1, labels.view(-1, 1), 1)


def _gradient(
    outputs, inputs, grad_outputs=None, retain_graph=None, create_graph=False
):
    """
    Compute the gradient of ``outputs`` with respect to ``inputs``
    gradient(x.sum(), x)
    gradient((x * y).sum(), [x, y])
    """
    if torch.is_tensor(inputs):
        inputs = [inputs]
    else:
        inputs = list(inputs)
    grads = torch.autograd.grad(
        outputs,
        inputs,
        grad_outputs,
        allow_unused=True,
        retain_graph=retain_graph,
        create_graph=create_graph,
    )
    grads = [x if x is not None else torch.zeros_like(y) for x, y in zip(grads, inputs)]
    return torch.cat([x.contiguous().view(-1) for x in grads])


def jacobian(outputs, inputs, create_graph=False):
    """
    Compute the Jacobian of ``outputs`` with respect to ``inputs``
    jacobian(x, x)
    jacobian(x * y, [x, y])
    jacobian([x * y, x.sqrt()], [x, y])

    Args:
        output: the output to calcualte the jacobainagainst
        inputs: the tensors to calculate the jacobian with respect to
        allow_unused (bool): allow input tensors not to be used in the grpah
        create_graph (bool): create a graph that can be used in the auto diff

    Example:
        >>> x = torch.randn(2,2, requires_grad=True)
        >>> y = torch.tensor([5.5, -4.], requires_grad=True)
        >>> j = jacobian(x.pow(y), [x, y])
    """
    if torch.is_tensor(outputs):
        outputs = [outputs]
    else:
        outputs = list(outputs)

    if torch.is_tensor(inputs):
        inputs = [inputs]
    else:
        inputs = list(inputs)

    jac = []
    for output in outputs:
        output_flat = output.view(-1)
        output_grad = torch.zeros_like(output_flat)
        for i in range(len(output_flat)):
            output_grad[i] = 1
            jac += [_gradient(output_flat, inputs, output_grad, True, create_graph)]
            output_grad[i] = 0
    return torch.stack(jac)


def hessian(output, inputs, out=None, allow_unused=False, create_graph=False):
    """
    Compute the Hessian of ``output`` with respect to ``inputs``
    hessian((x * y).sum(), [x, y])

    Args:
        output: the output to calcualte the hessian against
        inputs: the tensors to calculate the hessian with respect to
        allow_unused (bool): allow input tensors not to be used in the grpah
        create_graph (bool): create a graph that can be used in the auto diff


    Example:
        >>> x = torch.tensor([1.5, 2.5], requires_grad=True)
        >>> h = hessian(x.pow(2).prod(), x, create_graph=True)
    """
    assert output.ndimension() == 0

    if torch.is_tensor(inputs):
        inputs = [inputs]
    else:
        inputs = list(inputs)

    n = sum(p.numel() for p in inputs)
    if out is None:
        out = output.new_zeros(n, n)

    a_i = 0
    for i, inp in enumerate(inputs):
        [grad] = torch.autograd.grad(
            output, inp, create_graph=True, allow_unused=allow_unused
        )
        grad = torch.zeros_like(inp) if grad is None else grad
        grad = grad.contiguous().view(-1)

        for j in range(inp.numel()):
            if grad[j].requires_grad:
                row = _gradient(
                    grad[j], inputs[i:], retain_graph=True, create_graph=create_graph
                )[j:]
            else:
                row = grad[j].new_zeros(sum(x.numel() for x in inputs[i:]) - j)

            out[a_i, a_i:].add_(row.type_as(out))  # a_i's row
            if a_i + 1 < n:
                out[a_i + 1 :, a_i].add_(row[1:].type_as(out))  # a_i's column
            del row
            a_i += 1
        del grad

    return out
