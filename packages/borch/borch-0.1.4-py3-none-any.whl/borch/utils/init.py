"""
Functions to calculate values for different initialization strategies
"""
import math

import numpy as np


def _calculate_fan_in_and_fan_out(shape):
    if len(shape) < 2:
        raise ValueError(
            (
                "Fan in and fan out can not be computed for tensor "
                "with less than 2 dimensions"
            )
        )

    fan_out, fan_in, *kernel_shape = shape
    if kernel_shape:  # Convolutional layer
        kernel_size = np.prod(kernel_shape)
        fan_out *= kernel_size
        fan_in *= kernel_size

    return fan_in, fan_out


def _calculate_correct_fan(shape, mode):
    mode = mode.lower()
    valid_modes = ["fan_in", "fan_out"]
    if mode not in valid_modes:
        raise ValueError(
            "Mode {} not supported, please use one of {}".format(mode, valid_modes)
        )

    fan_in, fan_out = _calculate_fan_in_and_fan_out(shape)
    return fan_in if mode == "fan_in" else fan_out


def kaiming_normal_std(shape, slope=None, mode="fan_in", nonlinearity="linear"):
    r"""
    Callculates the standard deviation of a gaussian distribution according
    to the method described in in "Delving deep into rectifiers: Surpassing
    human-level performance on ImageNet classification" - He, K. et al.
    (2015), using a normal distribution. The resulting tensor will have values
     sampled from :math:``\mathcal{N}(0, \text{std})`` where

    .. math::
        \text{std} = \sqrt{\frac{2}{(1 + a^2) \times \text{fan_in}}}

    Also known as He initialization.


    Args:
        shape (tuple): a tuple with ints of shape of the tensor where the
          xavier init method will be used.
        slope: the negative slope of the rectifier used after this layer
            (sqrt(5) for leaky_relu by default)
        mode: either 'fan_in' (default) or 'fan_out'. Choosing ``fan_in``
            preserves the magnitude of the variance of the weights in the
            forward pass. Choosing ``fan_out`` preserves the magnitudes in the
            backwards pass.
        nonlinearity: the non-linear function (``nn.functional`` name),
            recommended to use only with 'relu' or 'leaky_relu' (default).

    Returns:
        float, the std to be used in a Gaussian Distribution to achieve a
         xavier initialization.

    Examples:
        >>> kaiming_normal_std((100, 100),nonlinearity="leaky_relu")
        0.057735026918962574...


    """
    if slope is None:
        slope = math.sqrt(5)

    if len(shape) < 2:
        shape = (1, *shape)
    fan = _calculate_correct_fan(shape, mode)
    gain = calculate_gain(nonlinearity, slope)
    std = gain / math.sqrt(fan)
    return std


def xavier_normal_std(shape, gain=1):
    r"""
    Callculates the standard deviation of a gaussian distribution according
    to the method described in "Understanding the difficulty of training deep
    feedforward neural networks" - Glorot, X. & Bengio, Y. (2010). The std
    can be used to construct a  :math:``\mathcal{N}(0, \text{std})``
    distribution,  where

    .. math::
        \text{std} = \text{gain} \times \sqrt{\frac{2}{\text{fan_in} +
        \text{fan_out}}}

    Also known as Glorot initialization.


    Args:
        shape (tuple): a tuple with ints of shape of the tensor where the
          xavier init method will be used.
        gain (float):  an optional scalingfan_out factor

    Returns:
        float, the std to be used in a Gaussian Distribution to achieve a xavier
         initialization.

    Examples:
        >>> xavier_normal_std((1000,))
        0.044699...

    """
    if len(shape) < 2:
        shape = (1, *shape)

    fan_in, fan_out = _calculate_fan_in_and_fan_out(shape)
    std = gain * math.sqrt(2.0 / (fan_in + fan_out))
    return std


def calculate_gain(nonlinearity, param=None):
    r"""Return the recommended gain value for the given nonlinearity function.
    The values are as follows:

    ================= ====================================================
    nonlinearity      gain
    ================= ====================================================
    Linear / Identity :math:``1``
    Conv{1,2,3}D      :math:``1``
    Sigmoid           :math:``1``
    Tanh              :math:``\frac{5}{3}``
    ReLU              :math:``\sqrt{2}``
    Leaky Relu        :math:``\sqrt{\frac{2}{1 + \text{negative_slope}^2}}``
    ================= ====================================================

    Args:
        nonlinearity: the non-linear function (``nn.functional`` name)
        param: optional parameter for the non-linear function

    Examples:
        >>> gain = calculate_gain('leaky_relu')
    """
    linear_fns = [
        "linear",
        "conv1d",
        "conv2d",
        "conv3d",
        "conv_transpose1d",
        "conv_transpose2d",
        "conv_transpose3d",
    ]
    if nonlinearity in linear_fns or nonlinearity == "sigmoid":
        return 1
    if nonlinearity == "tanh":
        return 5.0 / 3
    if nonlinearity == "relu":
        return math.sqrt(2.0)
    if nonlinearity == "leaky_relu":
        if param is None:
            negative_slope = 0.01
        elif (
            not isinstance(param, bool)
            and isinstance(param, int)
            or isinstance(param, float)
        ):
            # True/False are instances of int, hence check above
            negative_slope = param
        else:
            raise ValueError("negative_slope {} not a valid number".format(param))
        return math.sqrt(2.0 / (1 + negative_slope**2))
    raise ValueError("Unsupported nonlinearity {}".format(nonlinearity))
