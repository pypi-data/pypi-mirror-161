""""Posterior that uses only normal distributions"""
from borch.posterior.posterior import Posterior

from borch.distributions.distribution_utils import (
    normal_distribution_from_rv,
    scaled_normal_dist_from_rv,
)


class Normal(Posterior):
    r"""An automatic posterior which, when given a prior which is a continuous
    distribution, creates an approximating distribution
    :math:``\mathbb{N}(\mu, \sigma^2)``.

    Args:
        log_scale (float): The scale of the posterior will be initialized at
            exp(log_scale), where a ``torch.nn.Parameter`` is initialized at `log_scale`
            with the appropriate size.
        loc_at_prior_mean (bool): If one should initlize at the mean value of the prior
            or the current value of the prior if False.
    Examples:
        >>> import borch
        >>> import borch.distributions as dist
        >>> class Model(borch.Module):
        ...     def __init__(self):
        ...         super().__init__(posterior=Normal(log_scale=0))
        ...         self.student_t = dist.StudentT(3, 3, 4)
        ...         self.gamma = dist.Gamma(.5, .5)
        ...     def forward(self):
        ...         self.y = dist.Normal(self.student_t, self.gamma)
        ...         return self.y
        >>> model = Model()
        >>> type(model())
        <class 'torch.Tensor'>

        The posterior will be initialized as a ``Normal`` distribution with the
        scale set to ``1 (exp(0))``.

        >>> type(model.posterior.student_t)
        <class 'borch.distributions.rv_distributions.Normal'>
        >>> model.posterior.student_t.loc == model.prior.student_t.loc
        tensor(True)
        >>> float(model.posterior.student_t.scale)
        1.0

        However, the posterior distribution is only created the
        first time a ``RandomVariable`` gets added to the model it will not preform well
        for hierarchies. In this case it would mean that the ``loc`` of ``y`` is only
        set for the first forward and then optimized like a normal parameter after
        that. If one want to keep the hierarchy in the posterior as well one should
        use ``borch.posterior.Automatic`` or ``borch.posterior.Manual``.

        >>> model.posterior.y.loc == model.student_t
        tensor(True)
        >>> borch.sample(model)
        >>> model.posterior.y.loc == model.student_t
        tensor(False)
    """

    def __init__(self, log_scale=-3, loc_at_prior_mean=True):
        """
        Args:
            log_scale: Initial value of the log scale for approximating
              distributions.
        """
        super().__init__()
        self._log_scale = log_scale
        self.loc_at_prior_mean = loc_at_prior_mean

    def register_random_variable(self, name, rv):
        """Construct the q_distibution and add it to the ``Posterior``."""
        q_rv = normal_distribution_from_rv(
            rv, log_scale=self._log_scale, loc_at_mean=self.loc_at_prior_mean
        )
        setattr(self, name, q_rv)


class ScaledNormal(Posterior):
    r"""An automatic posterior which, when given a prior which is a continuous
    distribution, creates an approximating distribution
    :math:``\mathbb{N}(\mu, \sigma^2)`` where :math:\sigma^2 = scale*std(prior)``.

    The approximating distribution is initialised at current value of the RV if
    it is finite, otherwise a sample drawn from the prior is used.

    Args:
        scaling: value to multiply the stddev of the prior with to initialize
           the scale parameter of the posterior distribution.
        loc_at_prior_mean (bool): If one should initlize at the mean value
            of the prior or the current value of the prior if False.
    Examples:
        >>> import borch
        >>> import borch.distributions as dist
        >>> class Model(borch.Module):
        ...     def __init__(self):
        ...         super().__init__(posterior=ScaledNormal(scaling=.1))
        ...         self.student_t = dist.StudentT(3, 3, 4)
        ...         self.gamma = dist.Gamma(.5, .5)
        ...     def forward(self):
        ...         self.y = dist.Normal(self.student_t, self.gamma)
        ...         return self.y
        >>> model = Model()
        >>> type(model())
        <class 'torch.Tensor'>

        The posterior will be initialized as a ``Normal`` distribution with the
        scale set to ``scaling*prior.distribution.stddev``.

        >>> type(model.posterior.student_t)
        <class 'borch.distributions.rv_distributions.Normal'>
        >>> round(float(model.posterior.student_t.scale), 2)
        0.4

        However, the posterior distribution is only created the first time a
        ``RandomVariable`` gets added to the model it will not preform well
        for hierarchies. In this case it would mean that the ``loc`` of ``y`` is only
        set for the first forward and then optimized like a normal parameter after
        that. If one want to keep the hierarchy in the posterior as well one should
        use ``borch.posterior.Automatic`` or ``borch.posterior.Manual``.

        >>> model.posterior.y.loc == model.student_t
        tensor(True)
        >>> borch.sample(model)
        >>> model.posterior.y.loc == model.student_t
        tensor(False)
    """

    def __init__(self, scaling=0.01, loc_at_prior_mean=True):
        super().__init__()
        self._scaling = scaling
        self.loc_at_prior_mean = loc_at_prior_mean

    def register_random_variable(self, name, rv):
        setattr(
            self,
            name,
            scaled_normal_dist_from_rv(
                rv, scaling=self._scaling, loc_at_mean=self.loc_at_prior_mean
            ),
        )
