"""
Calculate different metrics such as accuracy and mean squared error.
"""
from operator import itemgetter

import numpy as np
from scipy.sparse import coo_matrix
import torch

# pylint: disable=unsubscriptable-object


def r2_mean_diff_ratio(pred, target):
    """Calculate r2

    Calculate the R2 using the mean difference ratio

    Args:
        pred (torch.tensor): the predicted values
        target (torch.tensor): the target

    Returns:
        a torch scalar with the R2
    """
    target_mean = torch.mean(target)
    pred_diff = torch.sum((pred - target_mean) ** 2)
    target_diff = torch.sum((target - target_mean) ** 2)
    return pred_diff / target_diff


def r2_score(pred, target):
    """Calculate r2 using the standard definition

    Args:
        pred (torch.tensor): the predicted values
        target (torch.tensor): the target

    Returns:
        a torch scalar with the R2

    """
    ss_res = torch.sum((target - pred) ** 2)
    ss_tot = torch.sum((pred - pred.mean()) ** 2)
    return 1 - ss_res / ss_tot


def mean_squared_error(pred, target):
    """
    Measures the averaged element-wise mean squared error.


    Args:
        pred (torch.tensor): the predicted values
        target (torch.tensor): the target

    Returns:
        a torch scalar with the MSE

    Examples:
        >>> import torch
        >>> mean_squared_error(torch.ones(2,3), torch.zeros(2,3))
        tensor(1.)
    """
    return ((pred - target) ** 2).mean()


def accuracy(pred, target):
    """
    Calculates the accuracy, i.e. how much agreement between two long tensors. It will
    return values between 0 and 1.

    Notes:
        This function does not support gradient trough it
    Args:
        pred (torch.tensor): the predicted values
        target (torch.tensor): the target

    Returns:
        a scalar with the calculated accuracy
    Examples:
        >>> import torch
        >>> accuracy(torch.tensor([2, 3]).long(), torch.tensor([2, 1]).long())
        tensor(0.5000)

    """
    return (target == pred).float().mean()


def accuracy_logit(logits, target):
    """
    Calculates the accuracy, between the arg max of a logit tensor and a target tensor.
    It will return values between 0 and 1.

    Notes:
        This function does not support gradient trough it
    Args:
        logits (torch.tensor): the predicted values
        target (torch.tensor): the target

    Returns:
        a scalar with the calculated accuracy

    Examples:
        >>> import torch
        >>> accuracy_logit(torch.ones(2, 2), torch.tensor([0, 1]).long())
        tensor(0.5000)
    """
    return (target == logits.argmax(-1)).float().mean()


def confusion_matrix(pred, target):
    """Compute confusion matrix to evaluate the accuracy of a classification
    By definition a confusion matrix :math:`C` is such that :math:`C_{i, j}`
    is equal to the number of observations known to be in group :math:`i` but
    predicted to be in group :math:`j`.
    Thus in binary classification, the count of true negatives is
    :math:`C_{0,0}`, false negatives is :math:`C_{1,0}`, true positives is
    :math:`C_{1,1}` and false positives is :math:`C_{0,1}`.

    Args:
        target(iterable, shape = [n_samples]): Ground truth (correct) target values.
        pred (iterable, shape = [n_samples]): Predicted Targets

    Returns:
        ``pandas.DataFrame``, shape = [n_classes, n_classes]: Confusion matrix

    Examples
    --------
    >>> y_true = [2, 0, 2, 2, 0, 1]
    >>> y_pred = [0, 0, 2, 2, 0, 2]
    >>> cm = confusion_matrix(y_pred, y_true)
    >>> y_true = ["cat", "ant", "cat", "cat", "ant", "bird"]
    >>> y_pred = ["ant", "ant", "cat", "cat", "ant", "cat"]
    >>> cm = confusion_matrix(y_pred, y_true)
    """

    if isinstance(target, torch.Tensor):
        target = target.flatten().tolist()

    if isinstance(pred, torch.Tensor):
        pred = pred.flatten().tolist()

    labels = np.array(sorted(list(set(target + pred))))
    n_labels = labels.size
    label_to_ind = {y: x for x, y in enumerate(labels)}
    # convert yt, yp into index
    pred = np.array([label_to_ind.get(x, n_labels + 1) for x in pred])
    target = np.array([label_to_ind.get(x, n_labels + 1) for x in target])
    sample_weight = np.ones(target.shape[0], dtype=np.float64)

    # intersect y_pred, y_true with labels, eliminate items not in labels
    # Pylint false flag
    # pylint: disable=assignment-from-no-return
    ind = np.logical_and(pred < n_labels, target < n_labels)
    pred, target, sample_weight = pred[ind], target[ind], sample_weight[ind]

    conf_mat = coo_matrix(
        (sample_weight, (target, pred)), shape=(n_labels, n_labels), dtype=np.float64
    ).toarray()
    conf_mat = conf_mat / conf_mat.sum(axis=1)[:, np.newaxis]
    return conf_mat, labels


def binary_roc_auc(preds, targets):
    """Compute the Area under the Receiver Operating Characteristics curve
    for a binary classification case.

    Args:
        targets (iterable, shape = [n_samples]): Ground truth (correct) target values.
        preds (iterable, shape = [n_samples]): Predicted Targets

    Returns:
        A scalar value representing the Area Under the ROC curve in percent

    Examples
    --------
    >>> y_pred = [0.9, 0.1, 0.2, 0.8, 0.7, 0.6]
    >>> y_true = [  0,   0,   1,   1,   0,   1]
    >>> binary_roc_auc(y_pred, y_true)
    0.4444444444444444
    """
    if not len(targets) == len(preds):
        raise RuntimeError("target shape and pred shape do not match.")

    # Check that targets contain both 0 and 1 (and nothing else)
    target_codomain = np.unique(targets)
    target_codomain.sort()
    if tuple(target_codomain) != (0, 1):
        raise RuntimeError("Targets must contain both 0 and 1 and nothing else. ")

    if min(preds) < 0 or max(preds) > 1:
        raise ValueError("Predictions must be in range [0, 1]")

    # pylint: disable=invalid-name
    m, n = 0, 0
    rank = []
    for pred, target in zip(preds, targets):
        if target > 0:
            m += 1
        else:
            n += 1
        rank.append((pred, target))
    rank.sort(key=itemgetter(0))

    r = 0
    for i, rank_ in enumerate(rank):
        if rank_[1] > 0:
            r += i
    u = r - m * (m - 1) / 2
    return u / (m * n)
