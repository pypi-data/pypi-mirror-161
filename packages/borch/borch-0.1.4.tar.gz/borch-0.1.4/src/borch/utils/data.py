"""
Tools to use datasets.
"""
from torch.utils.data import Dataset


class AddDatasetLength(Dataset):
    """Includes the length of the dataset when calling getitem"""

    def __init__(self, dataset):
        self.dataset = dataset
        self._len = len(dataset)

    def __getitem__(self, index):
        out = self.dataset[index]
        return self._len, out

    def __getattr__(self, item):
        return getattr(self.dataset, item)

    def __len__(self):
        return len(self.dataset)
