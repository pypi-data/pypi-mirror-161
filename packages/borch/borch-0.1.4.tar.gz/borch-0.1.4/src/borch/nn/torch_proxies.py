"""
Borch Proxies of PyTorch Modules
================================

This module exposes bayesian  versions of all PyTorch ``nn`` modules. Each module
can be used as it would be in PyTorch, but note that all parameters have now
been transformed into :class:``RandomVariable``.

Examples:
    >>> import torch
    >>> linear = torch.nn.Linear(3, 3)  # create a linear module
    >>> # Vanilla Linear has parameters for 'bias' and 'weight'
    >>> len(tuple(linear.parameters()))
    2
    >>> blinear = Linear(3, 3)
    >>> # The ppl proxy has ``RandomVariable`` s for each of these, each with
    >>> # their own parameters (2 when using Normal: loc, scale).
    >>> len(tuple(blinear.parameters()))
    4

    It follows the exact same syntax as ``torch.nn``, and can be mixed with
    existing ``torch.nn`` modules.
    >>> net = torch.nn.Sequential(Linear(3, 2), ReLU(), Linear(2,1))

    In order to get draw new samples for the ``RandomVariable`` s one need to use
    ``borch.sample``
    >>> import borch
    >>> out = net(torch.ones(1, 3))
    >>> borch.sample(net)
    >>> out ==  net(torch.ones(1, 3))
    tensor([[False]])

    To construct a variation inference loss for the ``RandomVariable`` s one simply
    >>> loss=borch.infer.vi_loss(**borch.pq_to_infer(net))
"""

# pylint: disable=protected-access,undefined-all-variable
import sys

from torch import nn

from borch.rv_factories import (
    kaiming_normal_rv,
    parameter_to_normal_rv,
)
from borch.utils.namespace_tools import extend_module
from borch.nn.borchify import borch_classes, BORCHIFY_REGISTRY

DOC_PREFIX = """This is a ppl class. Please see ``help(borch.nn)`` for more information.
If one gives distribution as kwargs, where names match the parameters of the Module, they
will be used as priors for those parameters.
"""


RV_FACTORIES = {
    "Linear": kaiming_normal_rv,
    "Bilinear": kaiming_normal_rv,
    "Conv1d": kaiming_normal_rv,
    "Conv2d": kaiming_normal_rv,
    "Conv3d": kaiming_normal_rv,
    "ConvTranspose1d": kaiming_normal_rv,
    "ConvTranspose2d": kaiming_normal_rv,
    "ConvTranspose3d": kaiming_normal_rv,
    "BatchNorm1d": None,
    "BatchNorm2d": None,
    "BatchNorm3d": None,
    "GRU": kaiming_normal_rv,
}


def get_rv_factory(cls_name):
    """
    Get the rv function corresponding to Module, if no
    custom rv_factory is defined, a defoult will be returned.
    Args:
        cls_name (sting): the name of the class we want the rv_factory for

    Returns:
        callable, an rv_factory
    """
    return RV_FACTORIES.get(cls_name, parameter_to_normal_rv)


_NO_WEIGHTS_MODULE_NAMES = [
    "AlphaDropout",
    "BCELoss",
    "BCEWithLogitsLoss",
    "BatchNorm1d",
    "BatchNorm2d",
    "BatchNorm3d",
    "CELU",
    "CTCLoss",
    "ChannelShuffle",
    "ChannelShuffle",
    "ConstantPad1d",
    "ConstantPad2d",
    "ConstantPad3d",
    "Container",
    "CosineEmbeddingLoss",
    "CrossEntropyLoss",
    "Dropout",
    "Dropout1d",
    "Dropout2d",
    "Dropout3d",
    "ELU",
    "FeatureAlphaDropout",
    "Flatten",
    "Fold",
    "GELU",
    "GLU",
    "GaussianNLLLoss",
    "Hardshrink",
    "Hardsigmoid",
    "Hardswish",
    "Hardtanh",
    "HingeEmbeddingLoss",
    "Identity",
    "InstanceNorm1d",
    "InstanceNorm2d",
    "InstanceNorm3d",
    "KLDivLoss",
    "L1Loss",
    "LeakyReLU",
    "LogSigmoid",
    "LogSoftmax",
    "Mish",
    "MSELoss",
    "MarginRankingLoss",
    "ModuleDict",
    "ModuleList",
    "MultiLabelMarginLoss",
    "MultiLabelSoftMarginLoss",
    "MultiMarginLoss",
    "MultiheadAttention",
    "NLLLoss",
    "NLLLoss2d",
    "PReLU",
    "PairwiseDistance",
    "ParameterDict",
    "ParameterList",
    "PixelShuffle",
    "PixelUnshuffle",
    "PoissonNLLLoss",
    "RReLU",
    "ReLU",
    "ReLU6",
    "ReflectionPad1d",
    "ReflectionPad2d",
    "ReplicationPad1d",
    "ReplicationPad2d",
    "ReplicationPad3d",
    "SELU",
    "Sequential",
    "SiLU",
    "Sigmoid",
    "SmoothL1Loss",
    "SoftMarginLoss",
    "Softmax",
    "Softmax2d",
    "Softmin",
    "Softplus",
    "Softshrink",
    "Softsign",
    "SyncBatchNorm",
    "Tanh",
    "Tanhshrink",
    "Threshold",
    "TripletMarginLoss",
    "TripletMarginWithDistanceLoss",
    "Unflatten",
    "Unfold",
    "Upsample",
    "UpsamplingBilinear2d",
    "UpsamplingNearest2d",
    "ZeroPad2d",
    "HuberLoss",
    "LazyBatchNorm1d",
    "LazyBatchNorm2d",
    "LazyBatchNorm3d",
    "LazyInstanceNorm1d",
    "LazyInstanceNorm2d",
    "LazyInstanceNorm3d",
    "ReflectionPad3d",
]


class _RNNFlatWeights:
    """Make sure we use getattr for the parameters"""

    @property
    def _flat_weights(self):
        return [
            (lambda wn: getattr(self, wn) if hasattr(self, wn) else None)(wn)
            for wn in self._flat_weights_names
        ]

    @_flat_weights.setter
    def _flat_weights(self, val):
        pass


def get_extra_baseclasses(cls):
    """Extra base classes for torch proxies"""
    if issubclass(cls, nn.RNNBase):
        return [_RNNFlatWeights]
    return []


_MAPPINGS = borch_classes(
    nn,
    get_rv_factory=get_rv_factory,
    doc_prefix=DOC_PREFIX,
    ignore=_NO_WEIGHTS_MODULE_NAMES,
    borchify_submodules=True,
    get_extra_baseclasses=get_extra_baseclasses,
    caller=__name__,
)
TORCH_BORCH_MAP = {mapping.original: mapping.augmented for mapping in _MAPPINGS}
BORCHIFY_REGISTRY.register(_MAPPINGS)
extend_module(__name__, _MAPPINGS)


NOT_BORCHIFIED = [
    getattr(nn, name) for name in _NO_WEIGHTS_MODULE_NAMES if hasattr(nn, name)
]
BORCHIFY_REGISTRY.register({v: v for v in NOT_BORCHIFIED})


for _cls in NOT_BORCHIFIED:
    setattr(sys.modules[__name__], _cls.__name__, _cls)


__all__ = [
    "AdaptiveAvgPool1d",
    "AdaptiveAvgPool2d",
    "AdaptiveAvgPool3d",
    "AdaptiveLogSoftmaxWithLoss",
    "AdaptiveMaxPool1d",
    "AdaptiveMaxPool2d",
    "AdaptiveMaxPool3d",
    "AlphaDropout",
    "AvgPool1d",
    "AvgPool2d",
    "AvgPool3d",
    "BCELoss",
    "BCEWithLogitsLoss",
    "BatchNorm1d",
    "BatchNorm2d",
    "BatchNorm3d",
    "Bilinear",
    "CELU",
    "CTCLoss",
    "ChannelShuffle",
    "ConstantPad1d",
    "ConstantPad2d",
    "ConstantPad3d",
    "Container",
    "Conv1d",
    "Conv2d",
    "Conv3d",
    "ConvTranspose1d",
    "ConvTranspose2d",
    "ConvTranspose3d",
    "CosineEmbeddingLoss",
    "CosineSimilarity",
    "CrossEntropyLoss",
    "CrossMapLRN2d",
    "DataParallel",
    "Dropout",
    "Dropout2d",
    "Dropout3d",
    "ELU",
    "Embedding",
    "EmbeddingBag",
    "FeatureAlphaDropout",
    "Flatten",
    "Fold",
    "FractionalMaxPool2d",
    "FractionalMaxPool3d",
    "GELU",
    "GLU",
    "GRU",
    "GRUCell",
    "GaussianNLLLoss",
    "GroupNorm",
    "Hardshrink",
    "Hardsigmoid",
    "Hardswish",
    "Hardtanh",
    "HingeEmbeddingLoss",
    "Identity",
    "InstanceNorm1d",
    "InstanceNorm2d",
    "InstanceNorm3d",
    "KLDivLoss",
    "L1Loss",
    "LPPool1d",
    "LPPool2d",
    "LSTM",
    "LSTMCell",
    "LayerNorm",
    "LazyConv1d",
    "LazyConv2d",
    "LazyConv3d",
    "LazyConvTranspose1d",
    "LazyConvTranspose2d",
    "LazyConvTranspose3d",
    "LazyLinear",
    "LeakyReLU",
    "Linear",
    "LocalResponseNorm",
    "LogSigmoid",
    "LogSoftmax",
    "MSELoss",
    "MarginRankingLoss",
    "MaxPool1d",
    "MaxPool2d",
    "MaxPool3d",
    "MaxUnpool1d",
    "MaxUnpool2d",
    "MaxUnpool3d",
    "ModuleDict",
    "ModuleList",
    "MultiLabelMarginLoss",
    "MultiLabelSoftMarginLoss",
    "MultiMarginLoss",
    "MultiheadAttention",
    "NLLLoss",
    "NLLLoss2d",
    "PReLU",
    "PairwiseDistance",
    "ParameterDict",
    "ParameterList",
    "PixelShuffle",
    "PixelUnshuffle",
    "PoissonNLLLoss",
    "RNN",
    "RNNBase",
    "RNNCell",
    "RNNCellBase",
    "RReLU",
    "ReLU",
    "ReLU6",
    "ReflectionPad1d",
    "ReflectionPad2d",
    "ReplicationPad1d",
    "ReplicationPad2d",
    "ReplicationPad3d",
    "SELU",
    "Sequential",
    "SiLU",
    "Sigmoid",
    "SmoothL1Loss",
    "SoftMarginLoss",
    "Softmax",
    "Softmax2d",
    "Softmin",
    "Softplus",
    "Softshrink",
    "Softsign",
    "SyncBatchNorm",
    "Tanh",
    "Tanhshrink",
    "Threshold",
    "Transformer",
    "TransformerDecoder",
    "TransformerDecoderLayer",
    "TransformerEncoder",
    "TransformerEncoderLayer",
    "TripletMarginLoss",
    "TripletMarginWithDistanceLoss",
    "Unflatten",
    "Unfold",
    "Upsample",
    "UpsamplingBilinear2d",
    "UpsamplingNearest2d",
    "ZeroPad2d",
]

_NEWER_MODULES = {
    "HuberLoss",
    "Dropout1d",
    "LazyBatchNorm1d",
    "LazyBatchNorm2d",
    "LazyBatchNorm3d",
    "LazyInstanceNorm1d",
    "LazyInstanceNorm2d",
    "LazyInstanceNorm3d",
    "Mish",
    "ReflectionPad3d",
}

# For backwards compatibility we can not have _NEWER_MODULES in __all__ as they might
# not exists in order versions of torch, use setattr on the sys.modules as
# any modifications to the `__all__` variable will breaks ide`s tab completion
setattr(
    sys.modules[__name__],
    "__all__",
    __all__ + list(_NEWER_MODULES.intersection(set(globals()))),
)
