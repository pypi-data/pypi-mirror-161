"""
Functions to 'borchify' PyTorch modules/networks.
"""
# pylint: disable=too-many-arguments
from typing import Optional
from copy import deepcopy
from functools import wraps

from torch.nn import Module
from torch import nn
from torch.distributions import Distribution

from borch.posterior import Posterior, Normal
from borch.utils.module_utils import copy_module_attributes
from borch.random_variable import RandomVariable
from borch import posterior as borch_posterior
from borch.module import Module as BorchModule, sample
from borch.rv_factories import (
    apply_rv_factory,
    parameter_to_normal_rv,
    priors_to_rv,
)
from borch.utils.func_tools import assign_docs
from borch.utils.namespace_tools import (
    create_augmented_classes,
    create_module,
)

PICKLE_CACHE = create_module("PICKLE_CACHE", "Cache of pickled modules")
_PICKLE_CACHE_PATH = f"{__name__}.PICKLE_CACHE"


def _get_priors_from_kwargs_(kwargs):
    priors = {}
    for key, val in kwargs.items():
        if isinstance(val, (Distribution, RandomVariable)):
            priors[key] = val
    for key in priors:
        kwargs.pop(key)
    return priors


def default_rv_factory(_):
    """Get the default random variable factory

    It creates a standard Gaussian.
    """
    return parameter_to_normal_rv


def borch_proxy_class(
    cls,
    get_rv_factory=default_rv_factory,
    doc_prefix="",
    borchify_submodules=False,
    get_extra_baseclasses=None,
    caller=None,
):
    """
    Create a Bayesian version of a `torch.nn.Module`

    Note that if the modules exists in `torch.nn` they will be replaced with the
    equivalent module from `borch.nn` instead of creating a new class.

    Args:
        cls: an uninstanciated class that is a subclass of `torch.nn.Module`
        get_rv_factory: function that takes a string as an argument and returns
           a function that creates random variables. See `borch.rv_factories`.
        doc_prefix (str): Extra documentation to append to the new class.
    """
    if cls in BORCHIFY_REGISTRY:
        return BORCHIFY_REGISTRY[cls]
    extra_inheriors = (
        get_extra_baseclasses(cls) if get_extra_baseclasses is not None else []
    )

    @wraps(cls.__init__)
    def _init(self, *args, posterior=None, **kwargs):
        # pylint: disable=redefined-outer-name
        if posterior is None:
            posterior = borch_posterior.Normal(loc_at_prior_mean=False)
        priors = _get_priors_from_kwargs_(kwargs)
        BorchModule.__init__(self, posterior=posterior)
        cls.__init__(self, *args, **kwargs)
        self.posterior = posterior
        rv_factory = get_rv_factory(cls.__name__)
        for key in priors:
            if key not in self._parameters:  # pylint: disable=protected-access
                raise ValueError(f"{key} does not match any parameters in the module")
        apply_rv_factory(
            self, lambda name, param: priors_to_rv(name, param, priors, rv_factory)
        )
        if borchify_submodules:
            _borchify_submodules_(self, rv_factory)
        sample(self, posterior=True, prior=True, redraw=False)

    new_cls = type(
        cls.__name__, (cls, BorchModule, *extra_inheriors), {"__init__": _init}
    )
    assign_docs(new_cls, cls, doc_prefix)
    caller = caller if caller is not None else _PICKLE_CACHE_PATH
    new_cls.__module__ = caller
    return new_cls


def borch_classes(
    module,
    get_rv_factory=default_rv_factory,
    doc_prefix="",
    ignore=None,
    parent=nn.Module,
    borchify_submodules=True,
    get_extra_baseclasses=None,
    caller=None,
):
    """
    Create a Bayesian version of classes in a python module.

    Note that if the modules exists in `torch.nn` they will be replaced with the
    equivalent module from `borch.nn` instead of creating a new class.

    Args:
        module: a python module that contains `torch.nn.Module`s you want a
                Bayesian version of.
        get_rv_factory: function that takes a string as an argument and returns
           a function that creates random variables. See `borch.rv_factories`.
        doc_prefix (str): Extra documentation to append to the new class.
        ignore (List(str)): List with string names of classes that should be skipped.
        parent (torch.nn.Module): a parent class you want to requite the subclasses
            to inherit from.
        borchify_submodules (bool): if submodules that are creates during the
            initialization method should also be borchified or not. Defaults to `False`.
    """
    ignore = ignore if ignore is not None else []
    mappings = create_augmented_classes(
        module=module,
        parent=parent,
        class_factory=lambda cls: borch_proxy_class(
            cls,
            get_rv_factory=get_rv_factory,
            doc_prefix=doc_prefix,
            borchify_submodules=borchify_submodules,
            get_extra_baseclasses=get_extra_baseclasses,
            caller=caller,
        ),
        ignore=ignore,
    )
    return mappings


def borchify_namespace(
    module,
    get_rv_factory=default_rv_factory,
    doc_prefix="",
    ignore=None,
    parent=nn.Module,
    borchify_submodules=True,
    get_extra_baseclasses=None,
):
    """
    Create a new module that contains bayesian versions of the `torch.nn.Module`s.

    Note that if the modules exists in `torch.nn` they will be replaced with the
    equivalent module from `borch.nn` instead of creating a new class.

    Args:
        module: a python module that contains `torch.nn.Module`s you want a
                Bayesian version of.
        get_rv_factory: function that takes a string as an argument and returns
           a function that creates random variables. See `borch.rv_factories`.
        doc_prefix (str): Extra documentation to append to the new class.
        ignore (List(str)): List with string names of classes that should be skipped.
        parent (torch.nn.Module): a parent class you want to requite the subclasses
            to inherit from.
        borchify_submodules (bool): if submodules that are creates during the
            initialization method should also be borchified or not. Defaults to `False`.

    Returns:
        A new python module where the `torch.nn.Modules` now also inherit from
        `borch.Module`.

    Examples:
        >>> import torch
        >>> bnn = borchify_namespace(torch.nn)
        >>> blinear = bnn.Linear(1,2)
        >>> type(blinear)
        <class 'borch.nn.torch_proxies.Linear'>
    """
    mappings = borch_classes(
        module=module,
        get_rv_factory=get_rv_factory,
        doc_prefix=doc_prefix,
        ignore=ignore,
        parent=parent,
        borchify_submodules=borchify_submodules,
        get_extra_baseclasses=get_extra_baseclasses,
    )
    classes = {mapping.name: mapping.augmented for mapping in mappings}
    namespace = dict(module.__dict__)
    namespace.update(classes)
    return create_module(module.__name__, module.__doc__, namespace)


def _instanciate(cls, *args, existing=None, **kwargs):
    """Instantiate a class without calling the init method"""
    obj = cls.__new__(cls, *args, **kwargs)
    if issubclass(cls, BorchModule):
        BorchModule.__init__(obj, *args, **kwargs)
    if existing is not None:
        copy_module_attributes(original=existing, new=obj)
    return obj


def _register_rvs_with_posterior(module):
    if hasattr(module, "prior"):
        for key in module.prior._modules.keys():  # pylint: disable=protected-access
            getattr(module, key, None)


class Registry:
    """Registry with mappings between different objects"""

    def __init__(self):
        self.registry = {}

    def register(self, kwargs, overwrite=False):
        """Register a new mapping"""
        if isinstance(kwargs, list):
            kwargs = {mapping.original: mapping.augmented for mapping in kwargs}
        overlap = set(self.registry).intersection(set(kwargs))
        if overlap and not overwrite:
            raise RuntimeError(f"{overlap} is already register")
        self.registry.update(kwargs)

    def __getitem__(self, key):
        return self.registry.get(key)

    def __contains__(self, key):
        return key in self.registry


BORCHIFY_REGISTRY = Registry()


def borchify_module(
    module: Module, rv_factory: Optional[callable] = None, posterior: Posterior = None
) -> BorchModule:
    """Take a ``Module`` instance and return a corresponding Borch
    equivalent.

    Args:
        module: The ``Module`` object to be 'borchified'.
        rv_factory: A callable which, when passed a ``Parameter``, returns a
          ``RandomVariable``, if None the default of ``borch.nn.borchify``
           will be used.
        posterior: A posterior for which the borchified module should use. The default
          is ``Normal`` (see ``borch.posterior``).

    Returns:
        A new module of type ``borch.Module``.

    Examples:
        >>> import torch
        >>> linear = torch.nn.Linear(3, 3)  # create a linear module
        >>> blinear = borchify_module(linear)
        >>> type(blinear)
        <class 'borch.nn.torch_proxies.Linear'>
    """
    # pylint: disable=unexpected-keyword-arg

    if posterior is None:
        posterior = Normal()
    if isinstance(module, BorchModule):
        new = deepcopy(module)
        new.posterior = posterior
        _register_rvs_with_posterior(new)
        return new

    cls_type = type(module)
    new_module = borch_proxy_class(cls_type)
    if not issubclass(new_module, BorchModule):
        return _instanciate(new_module, existing=module)
    new = _instanciate(new_module, existing=module, posterior=posterior)
    temp_rv_factory = (
        default_rv_factory(cls_type.__name__) if rv_factory is None else rv_factory
    )
    apply_rv_factory(new, temp_rv_factory)
    _register_rvs_with_posterior(new)
    return new


def borchify_network(
    module: Module,
    rv_factory: Optional[callable] = None,
    posterior_creator: callable = None,
    cache: dict = None,
) -> BorchModule:
    """Borchify a whole network. This applies ``borchify_module`` recursively on
    all modules within a network.

    Args:
        module: The network to be borchified.
        rv_factory: A callable which, when passed a ``Parameter``, returns a
          ``RandomVariable``, if None the default of ``borch.nn.borchify``
           will be used.
        posterior_creator: A callable which creates a posterior. This will be used to
          create a new posterior for each module in the network.
        cache: Cache is mapping from id(torch module) -> ppl module. Used to
          prevent double usage/recursion of borchification (NB recursive
          ``Module``s are actually not supported by PyTorch).

    Todo:
      * Specify which modules should be borchified.
      * Specify what random variable factories should be used where.

    Notes:
        Double use and recursion are respected. For example if a nested module
        appears in multiple locations in the original network, then the
        borchified version also uses the same borchified module in these
        locations.

    Returns:
        A new borchified network.

    Examples:
      >>> import torch
      >>>
      >>> class Net(Module):
      ...     def __init__(self):
      ...         super(Net, self).__init__()
      ...         self.linear = torch.nn.Linear(3,3)
      ...         # add a nested module
      ...         self.linear.add_module("nested", torch.nn.Linear(3,3))
      ...         self.sigmoid = torch.nn.Sigmoid()
      ...         self.linear2 = torch.nn.Linear(3,3)
      ...
      >>> net = Net()
      >>> bnet = borchify_network(net)
      >>> type(bnet)
      <class 'borch.nn.borchify.PICKLE_CACHE.Net'>
      >>> type(bnet.linear)
      <class 'borch.nn.torch_proxies.Linear'>
    """
    if cache is None:
        cache = {}

    _id = id(module)
    if _id in cache:
        return cache[_id]

    if posterior_creator is None:
        posterior_creator = lambda: Normal(-4, loc_at_prior_mean=False)
    new = borchify_module(module, rv_factory, posterior_creator())
    cache[_id] = new
    _borchify_submodules_(
        module,
        rv_factory=rv_factory,
        posterior_creator=posterior_creator,
        target=new,
        cache=cache,
    )
    return new


def _borchify_submodules_(
    module, rv_factory=None, posterior_creator=None, target=None, cache=None
):
    if target is None:
        target = module
    if cache is None:
        cache = {}
    for name, mod in module._modules.items():  # pylint: disable=protected-access
        if isinstance(module, BorchModule) and mod in module.internal_modules:
            continue
        adding = cache.get(
            id(mod), borchify_network(mod, rv_factory, posterior_creator, cache)
        )
        target.add_module(name, adding)
