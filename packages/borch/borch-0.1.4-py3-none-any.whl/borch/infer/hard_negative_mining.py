"""
Hard Negative Mining
====================

Exposes a function to perform hard negative mining, as defined in
:cite:`DBLP:journals/corr/LiuAESR15`.

"""

import math


def hard_negative_mining(losses, labels, neg_pos_ratio):
    """Suppress the presence of a large number of negative predictions.

    For any example, it keeps all the positive predictions and cuts the
    number of negative predictions so the ratio between the negative examples
    and positive examples is no more the given ratio.

    Args:
        losses (N, M): Predicted class probabilities for each example.
        labels (N, M): The class labels as one-hot encodings.
        neg_pos_ratio: The maximum ratio between negative and positive
          examples.

    Returns:
        Mask for applying to the loss.

    Example:
        >>> import torch
        >>> from borch.utils.torch_utils import one_hot
        >>>
        >>> losses = torch.rand(10, 5)
        >>> labels = one_hot(torch.randint(0, 5, (10,)), n_classes=5)
        >>> mask = hard_negative_mining(losses, labels, 3)
        >>> loss = losses[mask].sum()
    """
    pos_mask = labels > 0
    num_pos = pos_mask.long().sum(dim=1, keepdim=True)
    num_neg = num_pos * neg_pos_ratio

    losses[pos_mask] = -math.inf
    _, indexes = losses.sort(dim=1, descending=True)
    _, orders = indexes.sort(dim=1)
    neg_mask = orders < num_neg
    return pos_mask | neg_mask
