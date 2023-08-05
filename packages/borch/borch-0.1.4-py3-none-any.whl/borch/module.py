"""
Module
======

A ``torch.nn.Module`` that can handle the correct usage of ``borch.RandomVariable``.
When using ``__setattr__`` with a ``RandomVariable`` on a ``Module`` i.e.
``model.rv = borch.distributions.Normal(0, 1)``, it must be this ``borch.Module`` and
NOT a ``torch.nn.Module``

``borch.Module`` is a class from which all torch proxies are created and all
sub-classes of ``borch`` modules should inherit.

Examples:
    >>> import torch
    >>> import borch
    >>> from borch import distributions as dist
    >>> from borch.posterior import Normal

    >>>
    >>> class MyModule(Module):
    ...     def __init__(self, w_size):
    ...         super().__init__(posterior=Normal())
    ...         self.weight = dist.Normal(torch.ones(w_size), torch.ones(w_size))
    ...
    ...     def forward(self, x):
    ...         return x.matmul(self.weight)
    ...
    >>> my_module = MyModule(w_size=(4,))

    Set the values of random variable to be all 1s
    >>> my_module.observe(weight=torch.ones(4))
    >>> my_module(torch.ones((3, 4)))
    tensor([4., 4., 4.])

    To stop observing simply do
    >>> my_module.observe(weight=None)

    or to stop observing on all ``RandomVariable`` s directly attached to the module
    >>> my_module.observe(None)

    One can sample the ``RandomVariable`` s such that get new values
    >>> out = my_module(torch.ones((3, 4)))
    >>> borch.sample(my_module)
    >>> out == my_module(torch.ones((3, 4)))
    tensor([False, False, False])

    It is simple to construct the variational inference loss
    >>> loss = borch.infer.vi_loss(**pq_to_infer(my_module))
    >>> loss.backward()

    Access the prior for ``weight``
    >>> type(my_module.prior.weight)
    <class 'borch.distributions.rv_distributions.Normal'>
    >>> my_module.prior.weight.loc
    tensor([1., 1., 1., 1.])

    In the same way one can access the posterior for ``weight``
    >>> type(my_module.posterior.weight)
    <class 'borch.distributions.rv_distributions.Normal'>

"""
from functools import partial
import copy

from torch import Tensor
from torch.nn import Module as _Module

import borch


def _add_to_pq_dict(mod, _pq_dict, _seen):
    # pylint: disable=protected-access
    if mod in _seen or not isinstance(mod, Module):
        return
    _seen.add(mod)
    _pq_dict += [
        {
            "prior": getattr(mod.prior, name),
            "posterior": getattr(mod.posterior, name),
            "observed": name in mod.observed,
            "value": mod.observed[name]
            if name in mod.observed
            else getattr(mod.posterior, name).tensor,
        }
        for name in mod._used_rvs
    ]


def pq_dict(module) -> dict:
    """Create a dictionary where keys, values are prior distributions,
    approximating distributions, respectively.

    Returns:
        List with dicts where each dict contains the information about the
        prior, posterior and value

    Examples:
        >>> import torch
        >>> net = borch.nn.Linear(1,2)

        The pq_to_infer only returns information relating to ``RandomVariable`` s
        that has been accessed. So we just run the forward.
        >>> _= net(torch.randn(2, 1))
        >>> p_q = pq_dict(net)
        >>> list(p_q[0].keys())
        ['prior', 'posterior', 'observed', 'value']
    """
    out = []
    fn = partial(_add_to_pq_dict, _pq_dict=out, _seen=set())
    module.apply(fn)
    return out


def pq_to_infer(module):
    """
    Creats a dictionary of lists that can be used in ``borch.infer``
    Returns:
        dictionary with keys corresponding to arguments in
        infer.vi functions

    Examples:
        >>> import torch
        >>> net = borch.nn.Linear(1,2)

        The pq_to_infer only returns information relating to ``RandomVariable`` s
        that has been accessed. So we just run the forward.
        >>> _= net(torch.randn(2, 1))
        >>> p_q = pq_to_infer(net)

        Then we can use the result to construct a loss
        >>> loss = borch.infer.vi_loss(**p_q)
        >>> loss.backward()

    """
    p_q = pq_dict(module)
    # TODO can we change in input format in to infer?
    # Such we don't need to do this rearranging?
    return {
        "p_dists": [val["prior"] for val in p_q],
        "q_dists": [val["posterior"] for val in p_q],
        "values": [val["value"] for val in p_q],
        "observed": [val["observed"] for val in p_q],
    }


def sample(module, posterior=True, prior=False, redraw=True, memo=None):
    """Sample all RandomVariable in a network

    This is done by triggering a recalculation of each graph in the network

    Examples:
        >>> import torch
        >>> net = borch.nn.Linear(1,2)
        >>> out= net(torch.randn(2, 1))
        >>> sample(net)
        >>> out == net(torch.randn(2, 1))
        tensor([[False, False],
                [False, False]])
    """
    if memo is None:
        memo = set()
    if id(module) in memo:
        return

    def _recalculate(mod):
        if isinstance(mod, Module):
            mod._used_rvs.clear()  # pylint: disable=protected-access
        if isinstance(mod, borch.Graph):
            if redraw or not mod.has_been_run():
                mod()

    for name, mod in module.named_children():
        if (name == "prior" and not prior) or (name == "posterior" and not posterior):
            continue
        sample(mod, posterior=posterior, prior=prior, redraw=redraw, memo=memo)

    _recalculate(module)
    memo.update([id(module)])


def named_random_variables(module, posterior=True, prior=False):
    """Get all random variables"""
    for name, val in module.named_modules():
        if ("prior." in name and not prior) or ("posterior." in name and not posterior):
            continue  # pragma: no cover
        if isinstance(val, borch.RandomVariable):
            yield name, val


def random_variables(module, posterior=True, prior=False):
    """Generator to get all random variables from a network"""
    for _, val in named_random_variables(module, posterior=posterior, prior=prior):
        yield val


def set_posteriors(posterior_creator):
    """
    Function that takes any object and if it is a borch.nn.Module
    it sets the posterior to ``posterior_creator()' on that object.


    Args:
        posterior_creator (callable): should return a borch.posterior.posterior

    Examples:
        >>> from borch import posterior, nn, Module
        >>> model = Module(posterior=posterior.Normal())
        >>> model.lin = nn.Linear(10, 10)
        >>> _ = model.apply(set_posteriors(posterior.Automatic))
        >>> model.posterior
        Automatic()
    """

    def new_posterior(module):
        """sets a new posterior if a torch.Module"""
        if isinstance(module, Module):
            module.posterior = posterior_creator()
        else:
            pass

    return new_posterior


def unobserve(module):
    """Unobserve all values in all submodules"""

    def _unobserve(module):
        if isinstance(module, Module):
            module.observe(None)

    module.apply(_unobserve)


class Observed(_Module):
    """Used to store observed values in such it is part of the state dict"""

    # TODO should we aim to match the interface of a dict
    # or minimize the number of methods??
    def __setattr__(self, key, val):
        if isinstance(val, Tensor):
            if not hasattr(self, key):
                self.register_buffer(key, val)
        super().__setattr__(key, val)

    def update(self, kwargs):
        """Update the current state"""
        for key, val in kwargs.items():
            setattr(self, key, val)

    def delete(self, key):
        """delete an object from the state"""
        self.__delattr__(key)

    def __delitem__(self, key):
        self.__delattr__(key)

    def clear(self):
        """Remove all objects in the state"""
        self._buffers.clear()

    def get(self, key, default=None):
        """Get an object from the state"""
        return self._buffers.get(key, default)

    def __iter__(self):
        return iter(self._buffers.keys())

    def __contains__(self, key):
        return key in self._buffers

    def __getitem__(self, key):
        return self._buffers[key]

    def __setitem__(self, key, buffer):
        self.register_buffer(key, buffer)

    def items(self):
        """Get a key, value pair from the state"""
        return self._buffers.items()

    def pop(self, key):
        """return and remove an item from the state"""
        v = self[key]
        del self[key]
        return v

    @staticmethod
    def forward():
        """Don't use the forward"""
        raise RuntimeError(
            "This is a container for tensors and does not support a forward call"
        )


class Module(_Module):
    """Acts as a ``torch.nn.Module`` but handles ``borch.RandomVariable`` s correctly.

    It can be used in just the same way as in ``torch``
    >>> import torch
    >>> import borch
    >>> class MLP(Module):
    ...     def __init__(self, in_size, out_size):
    ...         super().__init__()
    ...         self.fc1 = borch.nn.Linear(in_size, in_size*2)
    ...         self.relu = borch.nn.ReLU()
    ...         self.fc2 = borch.nn.Linear(in_size*2, out_size)
    ...
    ...     def forward(self, x):
    ...         x = self.fc1(x)
    ...         x = self.relu(x)
    ...         x = self.fc2(x)
    ...
    >>> mlp = MLP(2, 2)
    >>> out = mlp(torch.randn(3, 2))

    It can be mixed with torch modules as one see fit.
    >>> class MLP2(Module):
    ...     def __init__(self, in_size, out_size):
    ...         super().__init__()
    ...         self.fc1 = torch.nn.Linear(in_size, in_size*2)
    ...         self.relu = torch.nn.ReLU()
    ...         self.fc2 = borch.nn.Linear(in_size*2, out_size)
    ...
    ...     def forward(self, x):
    ...         x = self.fc1(x)
    ...         x = self.relu(x)
    ...         x = self.fc2(x)
    ...
    >>> our = MLP2(2, 2)(torch.randn(3,2))

    The more interesting case is when one start to involve ``borch.RandomVariable`` s
    >>> from borch import distributions as dist
    >>> from borch.posterior import Normal
    >>> class MyModule(Module):
    ...     def __init__(self, w_size):
    ...         super().__init__(posterior=Normal())
    ...         self.weight = dist.Normal(torch.ones(w_size), torch.ones(w_size))
    ...
    ...     def forward(self, x):
    ...         return x.matmul(self.weight)
    ...
    >>> my_module = MyModule(w_size=(4,))


    Args:
        posterior: A ``borch.Posterior`` subclass that handles how the inference
                    is preformed.
    """

    # pylint: disable=abstract-method
    def __init__(self, posterior=None):
        super().__init__()
        if posterior is None:
            posterior = borch.posterior.Automatic()
        self.posterior = posterior
        self.prior = _Module()
        self.observed = Observed()
        self._used_rvs = set()

    @property
    def internal_modules(self):
        """Get the internal modules borch uses, like `prior`, `posterior`, `observed`"""
        return (self.posterior, self.prior, self.observed)

    def __deepcopy__(self, mmo):
        """Support `copy.deepcopy()`

        When using deepcopy, non leaf buffers will be coped and created as a new node,
        it is highly recommended to call `borch.sample` before using anything that has
        been copied.
        """
        new_instance = type(self).__new__(type(self))
        Module.__init__(new_instance)
        for k, v in self.__dict__.items():
            extra = {}
            if v is self._buffers:
                v = copy.copy(v)
                for _key, _val in list(v.items()):
                    if not _val.is_leaf:
                        extra[_key] = v[_key].clone() + 0
                        del v[_key]
            new = copy.deepcopy(v, mmo)
            if extra:
                new.update(extra)
            new_instance.__dict__[k] = new
        try:
            new_instance()
        except (NotImplementedError, TypeError):
            pass
        return new_instance

    def __copy__(self):
        return self.__deepcopy__({})

    def observe(self, *args, **kwargs):
        """Set/revert any random variables on the current posterior to be observed
        /latent.

        The behaviour of an observed variable means that any ``RandomVariable``
        objects assigned will be observed at the stated value (if the name
        matches a previously observed variable).

        Note:
            Calling ``observe' will overwrite all ``observe()`` calls made to ANY
            random variable attached to the module, even if it has a differnt name.
            One can still call ``observe`` on RandomVariable`` s in the forward after
            the ``observe`` call is made on the module.
        Args:
            args: If ``None``, all observed behaviour will be forgotten.
            kwargs: Any named arguments will be set to observed given that the
              value is a tensor, or the observed behaviour will be forgotten if
              set to ``None``.

        Examples:
            >>> import torch
            >>> from borch.distributions import Normal
            >>> from borch.posterior import Automatic
            >>>
            >>> model = Module()
            >>> rv = Normal(Tensor([1.]), Tensor([1.]))
            >>> model.observe(rv_one=Tensor([100.]))
            >>> model.rv_one = rv # rv_one has been observed
            >>> model.rv_one
            tensor([100.])
            >>> model.observe(None)  # stop observing rv_one, the value is no
            >>>                      # longer at 100.
            >>> sample(model)
            >>> torch.equal(model.rv_one, Tensor([100.]))
            False
        """
        if args or not kwargs:
            if len(args) != 1 or args[0] is not None:
                msg = "Invalid arguments: only None or kwargs allowed"
                raise ValueError(msg)
            for key in self.observed:
                rv = getattr(self.posterior, key, None)
                if rv is not None:
                    rv()  # redraw this sample
            self.observed.clear()

        not_tensor_or_none = [
            k for k, v in kwargs.items() if not isinstance(v, (Tensor, type(None)))
        ]
        if not_tensor_or_none:
            msg = (
                f"Received named arguments which are not one of"
                f" (None, torch.Tensor): {', '.join(not_tensor_or_none)}"
            )
            raise TypeError(msg)
        # update dictionary and remove None elements
        self.observed.update(kwargs)
        for k, v in tuple(self.observed.items()):
            if v is None:
                del self.observed[k]
                rv = getattr(self.posterior, k, None)
                if rv is not None:
                    rv()  # redraw this sample

    def get(self, name):
        """Standard `getattr` with no custom overloading"""
        return super().__getattr__(name)

    def __getattr__(self, name):
        try:
            return super().__getattr__(name)
        except AttributeError:
            posterior = self.__dict__.get("_modules", {}).get("posterior", None)
            prior = self.__dict__.get("_modules", {}).get("prior", None)
            if posterior is not None:
                param = getattr(self.posterior, name, None)
                if param is None and isinstance(
                    getattr(prior, name, None), borch.RandomVariable
                ):
                    self.posterior.set_random_variable(name, getattr(prior, name))
                    param = getattr(posterior, name)
                if isinstance(param, borch.RandomVariable):
                    observed = self.observed.get(name)
                    if observed is not None:
                        param.tensor = observed
                    self._used_rvs.add(name)
                    # we convert it to just a tensor here to avoid potential bugs
                    # in later pytorch releases we could potentially return the RV
                    return borch.as_tensor(param)

            raise AttributeError(
                "'{}' object has no attribute '{}'".format(type(self).__name__, name)
            )

    def __setattr__(self, name, value):
        if isinstance(value, borch.RandomVariable):
            if "_parameters" not in self.__dict__:
                msg = (
                    f"Cannot assign random variables before"
                    f" {type(self).__name__}.__init__() call"
                )
                raise AttributeError(msg)
            if hasattr(self, "posterior") and self.posterior is not None:
                self.posterior.set_random_variable(name, value)
            setattr(self.prior, name, value)
            self._used_rvs.add(name)
            self.__dict__.pop(name, None)
        else:
            super().__setattr__(name, value)
