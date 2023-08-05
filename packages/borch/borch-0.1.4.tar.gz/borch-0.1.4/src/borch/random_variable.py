"""
The base class for the RandomVariable primitive.

"""
import contextlib
import contextvars

from typing import Optional, Any, Union
import torch

import borch.graph as graph
import borch

_VALIDATE_ARGS = contextvars.ContextVar("VALIDATE_ARGS", default=None)


@contextlib.contextmanager
def validate_args(value):
    """
    Context manager that sets the `validate_args` for all random variable distributions.
    """
    _correct_validate_args_value(value)
    token = _VALIDATE_ARGS.set(value)
    try:
        yield
    finally:
        _VALIDATE_ARGS.reset(token)


def _correct_validate_args_value(value):
    if value is not None and not isinstance(value, bool):
        raise ValueError(
            f"`validate_args` must be one of True, False or None not {value}"
        )


class RandomVariable(graph.Graph):
    """Base class for a ``RandomVariable`` primitive used to model stochastic nodes.
    It merges a ``torch.tensor``, ``torch.nn.Module`` and
    a ``torch.distribution.Distributions``. It is not intended to be
    used directly but to be inherited from when creating a ``RandomVariable``.

    When used it will act as a ``torch.Tensor`` with a sample drawn from the
    distribution with most of the methods from a ``torch.nn.Module`` and
    a ``torch.distribution.Distributions``

    Examples:
        >>> import torch
        >>> import borch

        >>> class MyRV(RandomVariable):
        ...     distribution_cls = torch.distributions.Normal
        ...     def __init__(self, loc=1, scale=1):
        ...         super().__init__()
        ...         self.register_param_or_buffer("loc", loc)
        ...         self.register_param_or_buffer("scale", scale)
        ...         self()
        ...     def _distribution(self):
        ...         'Call that creates the torch distribution'
        ...         return self.distribution_cls(
        ...             borch.as_tensor(self.loc),
        ...             borch.as_tensor(self.scale)
        ...         )
        >>> rv = MyRV(torch.nn.Parameter(torch.tensor(1.)), 2.)

        It works as a normal tensor
        >>> torch.exp(rv) > 0
        tensor(True)

        One can also use the tensor attribute directly
        >>> type(rv.tensor)
        <class 'torch.Tensor'>
        >>> torch.exp(rv) == torch.exp(rv.tensor)
        tensor(True)

        The random variable have all the functionality from the ``torch.nn.Module``
        >>> list(rv.parameters())
        [Parameter containing:
        tensor(1., requires_grad=True)]
    """

    def __init__(
        self, validate_args=None, posterior=None
    ):  # pylint: disable=redefined-outer-name
        _correct_validate_args_value(validate_args)
        super().__init__(posterior=posterior)
        self._validate_args = validate_args

    @property
    def validate_args(self):
        """if the args should be validated when creating the distribution"""
        validate = self._validate_args if self._validate_args is not None else __debug__
        ctx_value = _VALIDATE_ARGS.get()
        return ctx_value if ctx_value is not None else validate

    @validate_args.setter
    def validate_args(self, value):
        """Set the value for validate_args"""
        _correct_validate_args_value(value)
        self._validate_args = value

    def __repr__(self):
        params = {**self._buffers, **self._modules, **self._parameters}
        tensor = params.pop(graph.TENSOR_ATTR)
        return (
            f"{self.__class__.__name__}: "
            + "".join([f"\n {key}: {repr(val)}" for key, val in params.items()])
            + f"\n tensor: {repr(tensor)}"
        )

    @property
    def distribution(self):
        """Create the ``torch.distributions.Distribution`` equivalent"""
        return self._distribution()

    def _distribution(self):
        """Overwrite this method with the call that creates the
        ``torch.distributions.Distribution``
        """
        raise NotImplementedError

    def distribution_cls(self):
        """Creator for the ``torch.distributions.Distribution``"""
        raise NotImplementedError

    def forward(self):
        """
        Draw a sample from the distribution
        """
        dist = self.distribution
        if dist.has_rsample:
            return dist.rsample()
        return dist.sample()

    @property
    def support(self) -> Optional[Any]:
        """
        Returns a :class:``~torch.distributions.constraints.Constraint`` object
        representing this distribution's support.
        """
        return self.distribution.support

    @property
    def has_rsample(self):
        """Check if rsample is implemented"""
        return self.distribution_cls.has_rsample

    @property
    def has_enumerate_support(self):
        """support enumerate"""
        return self.distribution_cls.has_enumerate_support

    def sample(self, sample_shape=torch.Size()):
        """
        Generates a sample_shape shaped sample or sample_shape shaped batch of
        samples if the distribution parameters are batched.
        """
        return self.distribution.sample(sample_shape)

    def rsample(self, sample_shape=torch.Size()):
        """
        Generates a sample_shape shaped reparameterized sample or sample_shape
        shaped batch of reparameterized samples if the distribution parameters
        are batched.
        """
        return self.distribution.rsample(sample_shape)

    def log_prob(self, value=None):
        """
        Returns the log of the probability density/mass function evaluated at
        ``value``.
        Args:
            value (Tensor):
        """
        value = value if value is not None else self.tensor
        return self.distribution.log_prob(value)

    def cdf(self, value=None):
        """
        Returns the cumulative density/mass function evaluated at
        ``value``.
        Args:
            value (Tensor):
        """
        value = value if value is not None else self.tensor
        return self.distribution.cdf(value)

    def icdf(self, value=None):
        """
        Returns the inverse cumulative density/mass function evaluated at
        ``value``.
        Args:
            value (Tensor):
        """
        value = value if value is not None else self.tensor
        return self.distribution.icdf(value)

    def entropy(self):
        """
        Returns entropy of distribution, batched over batch_shape.

        Returns:
            Tensor of shape batch_shape.
        """
        return self.distribution.entropy()

    def perplexity(self):
        """
        Returns perplexity of distribution, batched over batch_shape.
        Returns:
            Tensor of shape batch_shape.
        """
        return self.distribution.perplexity()


RVORDIST = Union[torch.distributions.Distribution, RandomVariable]


class RVPair(graph.Graph):
    """
    Provide a prior and the corresponding approximating
    distribution.

    This is useful when one wants a custom approximating
    distribution.
    """

    def __init__(self, p_dist, q_dist):
        posterior = borch.posterior.Manual()
        posterior.distribution = q_dist
        super().__init__(posterior=posterior)
        self.distribution = p_dist

    def forward(self):
        """The forward"""
        return self.distribution
