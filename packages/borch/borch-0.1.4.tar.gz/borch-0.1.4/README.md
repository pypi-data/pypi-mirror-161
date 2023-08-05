# Borch

[![pipeline status](https://gitlab.com/desupervised/borch/badges/master/pipeline.svg)](https://gitlab.com/desupervised/borch/-/commits/master)
[![coverage report](https://gitlab.com/desupervised/borch/badges/master/coverage.svg)](https://gitlab.com/desupervised/borch/-/commits/master)
[![lifecycle](https://img.shields.io/badge/lifecycle-maturing-blue?style=flat&link=https://lifecycle.r-lib.org/articles/stages.html)](https://lifecycle.r-lib.org/articles/stages.html)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![docs](https://img.shields.io/badge/docs-latest-green?style=flat&link=https://borch.readthedocs.io/en/latest/)](https://borch.readthedocs.io/en/latest/)

[Getting Started](https://borch.readthedocs.io/en/latest/tutorials/index.html) |
[Documentation](https://borch.readthedocs.io/en/latest/) |
[Contributing](https://gitlab.com/desupervised/borch/-/blob/master/CONTRIBUTING.md)

**Borch** is a universal probabilistic programming language (PPL) framework
developed by [Desupervised](https://desupervised.io/), that uses and integrates
with [PyTorch](https://pytorch.org/). Borch was designed with special attention
to support Bayesian neural networks in a native fashion. Further, it's designed
to

- Flexible and scalable framework
- Support neural networks out of the box.
- Have bells and whistles a universal PPL needs.

It can be installed with

```sh
pip install borch
```


## Usage

See our full tutorials
[here](https://borch.readthedocs.io/en/latest/tutorials/index.html).

As a quick example let's look into how the neural network interface looks. The
module `borch.nn` provides implementations of neural network modules that are
used for deep probabilistic programming and provides an interface almost
identical to the `torch.nn` modules. In many cases it is possible to just switch

```python
import torch.nn as nn
```

to

```python
import borch.nn as nn
```

and a network defined in torch is now probabilistic, without any other changes
in the model specification, one also need to change the loss function to
`infer.vi.vi_loss`.

For example, a convolutional neural network can be written as

```python
import torch
import torch.nn.functional as F
from borch import nn

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 6, 5)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = F.max_pool2d(F.relu(self.conv1(x)), (2, 2))
        x = F.max_pool2d(F.relu(self.conv2(x)), 2)
        x = x.view(-1, self.num_flat_features(x))
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

    def num_flat_features(self, x):
        size = x.size()[1:]
        num_features = 1
        for s in size:
            num_features *= s
        return num_features
```

## Installation

Borch can be installed using

```sh
pip install borch
```

## Docker

The Borch Docker images are available as both CPU and GPU versions at
[gitlab.com/desupervised/borch/container_registry](https://gitlab.com/desupervised/borch/container_registry/).
The latest CPU images can be used as

```sh
docker run registry.gitlab.com/desupervised/borch/cpu:master
```

## Contributing

Please read the contribution guidelines in `CONTRIBUTING.md`.

## Citation

If you use this software for your research or business please cite us and help
the package grow!

```text
@misc{borch,
  author = {Belcher, Lewis and Gudmundsson, Johan and Green, Michael},
  title = {Borch},
  howpublished = {https://gitlab.com/desupervised/borch},
  month        = "Apr",
  year         = "2021",
  note         = "v0.1.0",
  annote       = ""
}
```
