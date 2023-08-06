import numpy as np
import torch
from tifffile import imread
from torch.utils.data import ConcatDataset
from torchvision.datasets import VisionDataset


def reorder(src, target):
    """Get the indices of the target string letters in the source string.

    Such that src[reorder(src, target)] = target
    """
    return [src.index(i) for i in target]


def identity(item):
    return item


def load_volume(filepath):
    """Load a volume from a filepath.

    The volume is assumed to be in TIFF format, with axes in order TZCYX.
    It is return with axes reordered to CTZYX.

    Parameters
    ----------
    filepath: str
        The path to the volume

    Returns
    -------
    np.ndarray
        The volume
    """
    volume = imread(filepath)
    volume = np.transpose(volume, axes=reorder("TZCYX", "CTZYX"))
    return volume


class MabyDataset(VisionDataset):
    """
    Loading a tiff file in the MABY format.
    Combine to load multiple Tiff files using `torch.utils.data.ConcatDataset`

    Parameters
    ----------
    root: str
        The tif file name
    transform: torchvision.transforms.Transform
        Transform applied to both the source and target image
    source_transform: torchvision.transforms.Tranform
        Transform applied only to the target image
    target_transform: torchvision.transforms.Tranform
        Transform applied only to the target image
    """
    def __init__(self, root, transform=None, source_transform=None,
                 target_transform=None):
        super().__init__(root)
        self.transform = transform or identity
        self.source_transform = source_transform or identity
        self.target_transform = target_transform or identity
        self.volume = load_volume(root)

    def to_tensor(self, x):
        normed = x / x.max()
        standard = normed - 0.5 / 0.5
        return torch.from_numpy(standard.astype(np.float32))

    def get_all(self):
        """
        Return all the data in the dataset.

        Returns
        -------
        torch.Tensor
            The source image
        torch.Tensor
            The target image
        """
        x, y = [], []
        for i in range(len(self)):
            x_, y_ = self.__getitem__(i)
            x.append(x_)
            y.append(y_)
        return torch.stack(x), torch.stack(y)

    def _transform_one(self, x, y):
        x, y = (self.source_transform(self.to_tensor(x)),
                self.target_transform(y))
        return x, y

    def __getitem__(self, item):
        x, y = self.transform(self.volume[:, item])
        x, y = self._transform_one(x, y)
        return x, y

    def __len__(self):
        return self.volume.shape[1]


def load_data(data_directory, transform=None, source_transform=None,
              target_transform=None, split_validation=-1):
    """
    Load a dataset from a directory.

    Parameters
    ----------
    data_directory: str
        The directory containing the dataset
    transform: torchvision.transforms.Transform
        Transform applied to both the source and target image
    source_transform: torchvision.transforms.Tranform
        Transform applied only to the target image
    target_transform: torchvision.transforms.Tranform
        Transform applied only to the target image
    split_validation: int
        The number of files to use for validation.
        If -1, use all files in training, return no validation.

    Returns
    -------
    torch.utils.data.Dataset
        The dataset
    """
    datasets = [MabyDataset(filename, transform=transform,
                            target_transform=target_transform,
                            source_transform=source_transform)
                for filename in data_directory.iterdir()]
    if split_validation == -1:
        return ConcatDataset(datasets)
    else:
        train_dataset = ConcatDataset(datasets[:-split_validation])
        val_dataset = ConcatDataset(datasets[-split_validation:])
        return train_dataset, val_dataset
