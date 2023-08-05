"""Calculate the KL divergance between random variables."""
from torch import distributions as _dist
from torch.distributions.kl import _KL_REGISTRY

from borch.distributions.distribution_utils import as_distributions
from borch.random_variable import RVORDIST


def kl_divergence(p_dist, q_dist):
    # pylint: disable=line-too-long
    r"""
    Compute Kullback-Leibler divergence :math:`KL(p_dist \| q_dist)` between two distributions.

    .. math::

        KL(p_dist \| q_dist) = \int p_dist(x) \log\frac {p_dist(x)} {q_dist(x)} \,dx

    Args:
        p_dist (Distribution, RandomVariable): A :class:`~torch.distributions.Distribution` or `RandomVariable`.
        q_dist (Distribution, RandomVariable): A :class:`~torch.distributions.Distribution` or `RandomVariable`.

    Returns:
        Tensor: A batch of KL divergences of shape `batch_shape`.

    Raises:
        NotImplementedError: If the distribution types have not been registered via
            :meth:`register_kl`.
    """
    p_dist, q_dist = as_distributions(p_dist, q_dist)
    return _dist.kl_divergence(p_dist, q_dist)


KL_REGISTRY = {
    (key[0].__name__, key[1].__name__): val for key, val in _KL_REGISTRY.items()
}


def kl_exists(p_dist: RVORDIST, q_dist: RVORDIST) -> bool:
    """Determine whether the kl divergence is implemented between
    ``p_dist`` and ``q_dist``.

    Args:
        p_dist: Prior distribution.
        q_dist: Approximating distribution.

    Returns:
        True/False: whether kl divergence is defined.
    """
    p_dist, q_dist = as_distributions(p_dist, q_dist)
    key = (type(p_dist).__name__, type(q_dist).__name__)
    return KL_REGISTRY.get(key) is not None
