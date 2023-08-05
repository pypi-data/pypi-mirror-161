"""
RandomVariables for different `torch.distributions`
"""

from torch import distributions as _dist

from borch.distributions import distributions as bdist
from borch.random_variable import RandomVariable
from borch.graph import as_tensor
from borch.utils.func_tools import disable_doctests

# pylint: disable=missing-class-docstring,unexpected-keyword-arg,abstract-method,too-many-function-args,too-many-arguments


class _LocScaleArgs(RandomVariable):
    def __init__(self, loc, scale, validate_args=None, posterior=None):
        super().__init__(validate_args=validate_args, posterior=posterior)
        self.register_param_or_buffer("loc", loc)
        self.register_param_or_buffer("scale", scale)

    def _distribution(self):
        return self.distribution_cls(
            as_tensor(self.loc), as_tensor(self.scale), validate_args=self.validate_args
        )


class _ScaleArg(RandomVariable):
    def __init__(self, scale, validate_args=None, posterior=None):
        super().__init__(validate_args=validate_args, posterior=posterior)
        self.register_param_or_buffer("scale", scale)

    def _distribution(self):
        return self.distribution_cls(
            as_tensor(self.scale), validate_args=self.validate_args
        )


class HalfCauchy(_ScaleArg):
    distribution_cls = _dist.HalfCauchy
    __doc__ = disable_doctests(distribution_cls.__doc__)


class HalfNormal(_ScaleArg):
    distribution_cls = _dist.HalfNormal
    __doc__ = disable_doctests(distribution_cls.__doc__)


class _ProbsLogitsArgs(RandomVariable):
    def __init__(self, probs=None, logits=None, validate_args=None, posterior=None):
        super().__init__(validate_args=validate_args, posterior=posterior)
        _check_only_one(probs=probs, logits=logits)
        self.register_param_or_buffer("probs", probs)
        self.register_param_or_buffer("logits", logits)

    def _distribution(self):
        return self.distribution_cls(
            probs=as_tensor(self.probs),
            logits=as_tensor(self.logits),
            validate_args=self.validate_args,
        )


class Normal(_LocScaleArgs):
    """Normal distributed random variable"""

    distribution_cls = _dist.Normal
    __doc__ = disable_doctests(distribution_cls.__doc__)


class Cauchy(_LocScaleArgs):
    distribution_cls = _dist.Cauchy
    __doc__ = disable_doctests(distribution_cls.__doc__)


class Gumbel(_LocScaleArgs):
    distribution_cls = _dist.Gumbel
    __doc__ = disable_doctests(distribution_cls.__doc__)


class LogNormal(_LocScaleArgs):
    distribution_cls = _dist.LogNormal
    __doc__ = disable_doctests(distribution_cls.__doc__)


class Laplace(_LocScaleArgs):
    distribution_cls = _dist.Laplace
    __doc__ = disable_doctests(distribution_cls.__doc__)


class Bernoulli(_ProbsLogitsArgs):
    distribution_cls = _dist.Bernoulli
    __doc__ = disable_doctests(distribution_cls.__doc__)


class Categorical(_ProbsLogitsArgs):
    distribution_cls = _dist.Categorical
    __doc__ = disable_doctests(distribution_cls.__doc__)


class Geometric(_ProbsLogitsArgs):
    distribution_cls = _dist.Geometric
    __doc__ = disable_doctests(distribution_cls.__doc__)


class OneHotCategorical(_ProbsLogitsArgs):
    distribution_cls = _dist.OneHotCategorical
    __doc__ = disable_doctests(distribution_cls.__doc__)


class StudentT(RandomVariable):
    distribution_cls = _dist.StudentT
    __doc__ = disable_doctests(distribution_cls.__doc__)

    def __init__(self, df, loc, scale, validate_args=None, posterior=None):
        super().__init__(validate_args=validate_args, posterior=posterior)
        self.register_param_or_buffer("df", df)
        self.register_param_or_buffer("loc", loc)
        self.register_param_or_buffer("scale", scale)

    def _distribution(self):
        return self.distribution_cls(
            as_tensor(self.df),
            as_tensor(self.loc),
            as_tensor(self.scale),
            validate_args=self.validate_args,
        )


class Pareto(RandomVariable):
    distribution_cls = _dist.Pareto
    __doc__ = disable_doctests(distribution_cls.__doc__)

    def __init__(self, scale, alpha, validate_args=None, posterior=None):
        super().__init__(validate_args=validate_args, posterior=posterior)
        self.register_param_or_buffer("scale", scale)
        self.register_param_or_buffer("alpha", alpha)

    def _distribution(self):
        return self.distribution_cls(
            as_tensor(self.scale),
            as_tensor(self.alpha),
            validate_args=self.validate_args,
        )


def _check_only_one(**kwargs):
    not_none = [val for val in kwargs.values() if val is not None]
    if len(not_none) > 1:
        raise ValueError(f"One and only one of {list(kwargs)} can be provided.")


class _Binomial(RandomVariable):
    def __init__(
        self, total_count, probs=None, logits=None, validate_args=None, posterior=None
    ):
        super().__init__(validate_args=validate_args, posterior=posterior)
        _check_only_one(probs=probs, logits=logits)
        self.register_param_or_buffer("total_count", total_count)
        self.register_param_or_buffer("probs", probs)
        self.register_param_or_buffer("logits", logits)

    def _distribution(self):
        return self.distribution_cls(
            total_count=as_tensor(self.total_count),
            probs=as_tensor(self.probs),
            logits=as_tensor(self.logits),
            validate_args=self.validate_args,
        )


class Binomial(_Binomial):
    distribution_cls = _dist.Binomial
    __doc__ = disable_doctests(distribution_cls.__doc__)


class NegativeBinomial(_Binomial):
    distribution_cls = _dist.NegativeBinomial
    __doc__ = disable_doctests(distribution_cls.__doc__)


class Multinomial(RandomVariable):
    distribution_cls = _dist.Multinomial
    __doc__ = disable_doctests(distribution_cls.__doc__)

    def __init__(
        self, total_count, probs=None, logits=None, validate_args=None, posterior=None
    ):
        super().__init__(validate_args=validate_args, posterior=posterior)
        _check_only_one(probs=probs, logits=logits)
        self.register_param_or_buffer("total_count", total_count)
        self.register_param_or_buffer("probs", probs)
        self.register_param_or_buffer("logits", logits)

    def _distribution(self):
        return self.distribution_cls(
            total_count=int(self.total_count),
            probs=as_tensor(self.probs),
            logits=as_tensor(self.logits),
            validate_args=self.validate_args,
        )


class Gamma(RandomVariable):
    distribution_cls = _dist.Gamma
    __doc__ = disable_doctests(distribution_cls.__doc__)

    def __init__(self, concentration, rate, validate_args=None, posterior=None):
        super().__init__(validate_args=validate_args, posterior=posterior)
        self.register_param_or_buffer("concentration", concentration)
        self.register_param_or_buffer("rate", rate)

    def _distribution(self):
        return self.distribution_cls(
            as_tensor(self.concentration),
            as_tensor(self.rate),
            validate_args=self.validate_args,
        )


class LKJCholesky(RandomVariable):
    distribution_cls = _dist.LKJCholesky
    __doc__ = disable_doctests(distribution_cls.__doc__)

    def __init__(self, dimension, concentration, validate_args=None, posterior=None):
        super().__init__(validate_args=validate_args, posterior=posterior)
        self.register_param_or_buffer("concentration", concentration)
        self.register_param_or_buffer("dimension", dimension)

    def _distribution(self):
        return self.distribution_cls(
            int(self.dimension),
            as_tensor(self.concentration),
            validate_args=self.validate_args,
        )


class Dirichlet(RandomVariable):
    distribution_cls = _dist.Dirichlet
    __doc__ = disable_doctests(distribution_cls.__doc__)

    def __init__(self, concentration, validate_args=None, posterior=None):
        super().__init__(validate_args=validate_args, posterior=posterior)
        self.register_param_or_buffer("concentration", concentration)

    def _distribution(self):
        return self.distribution_cls(
            as_tensor(self.concentration), validate_args=self.validate_args
        )


class _RateArg(RandomVariable):
    def __init__(self, rate, validate_args=None, posterior=None):
        super().__init__(validate_args=validate_args, posterior=posterior)
        self.register_param_or_buffer("rate", rate)

    def _distribution(self):
        return self.distribution_cls(
            as_tensor(self.rate), validate_args=self.validate_args
        )


class Exponential(_RateArg):
    distribution_cls = _dist.Exponential
    __doc__ = disable_doctests(distribution_cls.__doc__)


class Poisson(_RateArg):
    distribution_cls = _dist.Poisson
    __doc__ = disable_doctests(distribution_cls.__doc__)


class Chi2(RandomVariable):
    distribution_cls = _dist.Chi2
    __doc__ = disable_doctests(distribution_cls.__doc__)

    def __init__(self, df, validate_args=None, posterior=None):
        super().__init__(validate_args=validate_args, posterior=posterior)
        self.register_param_or_buffer("df", df)

    def _distribution(self):
        return self.distribution_cls(
            as_tensor(self.df), validate_args=self.validate_args
        )


class FisherSnedecor(RandomVariable):
    distribution_cls = _dist.FisherSnedecor
    __doc__ = disable_doctests(distribution_cls.__doc__)

    def __init__(self, df1, df2, validate_args=None, posterior=None):
        super().__init__(validate_args=validate_args, posterior=posterior)
        self.register_param_or_buffer("df1", df1)
        self.register_param_or_buffer("df2", df2)

    def _distribution(self):
        return self.distribution_cls(
            as_tensor(self.df1), as_tensor(self.df2), validate_args=self.validate_args
        )


class _Concentraton1Concentration0Args(RandomVariable):
    def __init__(
        self, concentration1, concentration0, validate_args=None, posterior=None
    ):
        super().__init__(validate_args=validate_args, posterior=posterior)
        self.register_param_or_buffer("concentration0", concentration0)
        self.register_param_or_buffer("concentration1", concentration1)

    def _distribution(self):
        return self.distribution_cls(
            as_tensor(self.concentration1),
            as_tensor(self.concentration0),
            validate_args=self.validate_args,
        )


class Beta(_Concentraton1Concentration0Args):
    distribution_cls = _dist.Beta
    __doc__ = disable_doctests(distribution_cls.__doc__)


class Kumaraswamy(_Concentraton1Concentration0Args):
    distribution_cls = _dist.Kumaraswamy
    __doc__ = disable_doctests(distribution_cls.__doc__)


class Uniform(RandomVariable):
    distribution_cls = _dist.Uniform
    __doc__ = disable_doctests(distribution_cls.__doc__)

    def __init__(self, low, high, validate_args=None, posterior=None):
        super().__init__(validate_args=validate_args, posterior=posterior)
        self.register_param_or_buffer("low", low)
        self.register_param_or_buffer("high", high)

    def _distribution(self):
        return self.distribution_cls(
            as_tensor(self.low), as_tensor(self.high), validate_args=self.validate_args
        )


class PointMass(RandomVariable):
    distribution_cls = bdist.PointMass
    __doc__ = disable_doctests(distribution_cls.__doc__)

    def __init__(self, value, support, posterior=None):
        super().__init__(posterior=posterior)
        self.register_param_or_buffer("value", value)
        self._support = support

    def _distribution(self):
        return self.distribution_cls(
            as_tensor(self.value), self._support, validate_args=self.validate_args
        )


class Delta(RandomVariable):
    distribution_cls = bdist.Delta
    __doc__ = disable_doctests(distribution_cls.__doc__)

    def __init__(self, value, posterior=None):
        super().__init__(posterior=posterior)
        self.register_param_or_buffer("value", value)

    def _distribution(self):
        return self.distribution_cls(
            as_tensor(self.value), validate_args=self.validate_args
        )


class TransformedDistribution(RandomVariable):
    distribution_cls = _dist.TransformedDistribution
    __doc__ = disable_doctests(distribution_cls.__doc__)

    def __init__(
        self, base_distribution, transforms, validate_args=None, posterior=None
    ):
        super().__init__(validate_args=validate_args, posterior=posterior)
        # NB use add_module instead of setattr, as we don't want this added to
        # the prior and posterior
        self.add_module("base_distribution", base_distribution)
        self.transforms = transforms

    def _distribution(self):
        return self.distribution_cls(
            self.get("base_distribution").distribution,
            self.transforms,
            validate_args=self.validate_args,
        )


class MultivariateNormal(RandomVariable):
    distribution_cls = _dist.MultivariateNormal
    __doc__ = disable_doctests(distribution_cls.__doc__)

    def __init__(
        self,
        loc,
        covariance_matrix=None,
        precision_matrix=None,
        scale_tril=None,
        validate_args=None,
        posterior=None,
    ):
        _check_only_one(
            covariance_matrix=covariance_matrix,
            scale_tril=scale_tril,
            precision_matrix=precision_matrix,
        )
        super().__init__(validate_args=validate_args, posterior=posterior)
        self.register_param_or_buffer("loc", loc)
        self.register_param_or_buffer("covariance_matrix", covariance_matrix)
        self.register_param_or_buffer("precision_matrix", precision_matrix)
        self.register_param_or_buffer("scale_tril", scale_tril)

    def _distribution(self):
        return self.distribution_cls(
            as_tensor(self.loc),
            as_tensor(self.covariance_matrix),
            as_tensor(self.precision_matrix),
            as_tensor(self.scale_tril),
            validate_args=self.validate_args,
        )


class _TemperatureProbsLogitsArgs(RandomVariable):
    def __init__(
        self, temperature, probs=None, logits=None, validate_args=None, posterior=None
    ):
        super().__init__(validate_args=validate_args, posterior=posterior)
        _check_only_one(probs=probs, logits=logits)
        self.register_param_or_buffer("temperature", temperature)
        self.register_param_or_buffer("probs", probs)
        self.register_param_or_buffer("logits", logits)

    def _distribution(self):
        return self.distribution_cls(
            temperature=as_tensor(self.temperature),
            probs=as_tensor(self.probs),
            logits=as_tensor(self.logits),
            validate_args=self.validate_args,
        )


class RelaxedBernoulli(_TemperatureProbsLogitsArgs):
    distribution_cls = _dist.RelaxedBernoulli
    __doc__ = disable_doctests(distribution_cls.__doc__)


class RelaxedOneHotCategorical(_TemperatureProbsLogitsArgs):
    distribution_cls = _dist.RelaxedOneHotCategorical
    __doc__ = disable_doctests(distribution_cls.__doc__)


class VonMises(RandomVariable):
    distribution_cls = _dist.VonMises
    __doc__ = disable_doctests(distribution_cls.__doc__)

    def __init__(self, loc, concentration, validate_args=None, posterior=None):
        super().__init__(validate_args=validate_args, posterior=posterior)
        self.register_param_or_buffer("loc", loc)
        self.register_param_or_buffer("concentration", concentration)

    def _distribution(self):
        return self.distribution_cls(
            as_tensor(self.loc),
            as_tensor(self.concentration),
            validate_args=self.validate_args,
        )


class Weibull(RandomVariable):
    distribution_cls = _dist.Weibull
    __doc__ = disable_doctests(distribution_cls.__doc__)

    def __init__(self, scale, concentration, validate_args=None, posterior=None):
        super().__init__(validate_args=validate_args, posterior=posterior)
        self.register_param_or_buffer("scale", scale)
        self.register_param_or_buffer("concentration", concentration)

    def _distribution(self):
        return self.distribution_cls(
            as_tensor(self.scale),
            as_tensor(self.concentration),
            validate_args=self.validate_args,
        )
