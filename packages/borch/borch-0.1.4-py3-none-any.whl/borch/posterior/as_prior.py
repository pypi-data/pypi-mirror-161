"""Form an approximating posterior that looks just like the priors"""

from borch.posterior.posterior import Posterior

from borch.distributions.distribution_utils import (
    dist_to_qdist,
)


class AsPrior(Posterior):
    """A posterior for variational inference that  will add approximating
    `RandomVariable`s based on the `RandomVariable` that gets register.

    It will use the same type of distribution as the prior and initialize the
    variables in the same point as the prior.

    Examples:
        >>> import borch
        >>> import borch.distributions as dist
        >>> class Model(borch.Module):
        ...     def __init__(self):
        ...         super().__init__(posterior=AsPrior())
        ...         self.student_t = dist.StudentT(3, 3, 4)
        ...         self.gamma = dist.Gamma(.5, .5)
        ...     def forward(self):
        ...         self.y = dist.Normal(self.student_t, self.gamma)
        ...         return self.y
        >>> model = Model()
        >>> type(model())
        <class 'torch.Tensor'>

        The posterior will be initialized with the same type of distribution
        and the same values for the parameters.

        >>> type(model.posterior.student_t)
        <class 'borch.distributions.rv_distributions.StudentT'>
        >>> model.posterior.student_t.loc == model.prior.student_t.loc
        tensor(True)
        >>> model.posterior.student_t.scale == model.prior.student_t.scale
        tensor(True)

        However, the posterior distribution is only created the first time
        a ``RandomVariable`` gets added to the model it will not preform well
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

    def register_random_variable(self, name, rv):
        """A passed ``RandomVariable`` will be cloned and an appropriate
        approximating distribution will be returned in its place, based on
        whether the given `rv` had an approximating distribution or not."""
        setattr(self, name, dist_to_qdist(rv))
