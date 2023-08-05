"""Posterior that creates a PointMass distribution for all parameters"""

from torch.nn import Parameter
from torch.distributions.constraint_registry import transform_to

from borch.posterior.posterior import Posterior
from borch import distributions as dist


class PointMass(Posterior):
    """A posterior that is used to operate on unconstrained parameter values,
    intended to be used with MCMC.

    The `PointMass` posterior creates a `borch.distributions.distributions.PointMass`
    as the approximating distribution. That means it will be a parameter that is
    constrained to be on the same support as the prior. So unless one update the
    values of the parameters ex. using an optimizer. The `RandomVariable`s will
    have the same value after getting sampled.


    Examples:
        >>> import borch
        >>> import borch.distributions as dist
        >>> class Model(borch.Module):
        ...     def __init__(self):
        ...         super().__init__(posterior=PointMass())
        ...         self.student_t = dist.StudentT(3, 3, 4)
        ...         self.gamma = dist.Gamma(.5, .5)
        ...     def forward(self):
        ...         self.y = dist.Normal(self.student_t, self.gamma)
        ...         return self.y
        >>> model = Model()
        >>> type(model())
        <class 'torch.Tensor'>
        >>> gamma = float(model.gamma)
        >>> borch.sample(model)
        >>> float(model.gamma) == gamma
        True

    """

    def register_q_random_variable(self, name, p_rv, q_rv):
        """Allow the user to directly comunicate with the posterior of what q_dist
        to use"""
        if not isinstance(q_rv, dist.PointMass):
            raise ValueError(
                "Only PointMass distributions can be added to the posterior"
            )
        setattr(self, name, q_rv)

    def register_random_variable(self, name, rv):
        """Register a random variable with the posterior"""
        u_val = Parameter(transform_to(rv.support).inv(rv.sample()).detach())
        new = dist.PointMass(u_val, rv.support)
        setattr(self, name, new)
