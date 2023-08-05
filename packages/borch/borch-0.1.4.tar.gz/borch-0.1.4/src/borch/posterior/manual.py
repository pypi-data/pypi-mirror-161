"""Posterior that allows one to manually express the variational posterior

"""
from borch.posterior.posterior import Posterior


class Manual(Posterior):
    """The manual posterior must have all `RandomVariable` objects explicitly added
    before they are available for use in a Model.

    Notes:
        Adding a `RVPair` will add the approximating `RandomVariable` to the posterior
        will raise an error.

    Examples:
        >>> import torch
        >>> import borch
        >>> import borch.distributions as dist
        >>> class ManualPosterior(Manual):
        ...     def __init__(self):
        ...         super().__init__()
        ...         self.loc = torch.nn.Parameter(torch.randn(1))
        ...         self.scale = torch.nn.Parameter(torch.randn(1))
        ...     def forward(self):
        ...         self.student_t = dist.StudentT(3, self.loc, torch.exp(self.scale))
        ...         self.y = dist.Normal(self.student_t, .3)
        ...         return self.y
        >>> manual_posterior = ManualPosterior()
        >>> class Model(borch.Module):
        ...     def __init__(self, posterior):
        ...         super().__init__(posterior=posterior)
        ...         self.student_t = dist.StudentT(3, 3, 4)
        ...     def forward(self):
        ...         self.y = dist.Normal(self.student_t, .3)
        ...         return self.y

        In order to use the posterior properly, it is important to remember to first run
        the forward of manual posterior before running the forward of the model.

        >>> _ = manual_posterior()
        >>> model = Model(manual_posterior)
        >>> type(model())
        <class 'torch.Tensor'>

    """

    def register_random_variable(self, name, rv):
        """Just add the rv to the posterior"""

        raise RuntimeError(
            f"""Attempted to add a random variable named `{name}` to Manual posterior
            using `register_random_variable`. Need to use `setattr`
            and do it manually first.
            """
        )
