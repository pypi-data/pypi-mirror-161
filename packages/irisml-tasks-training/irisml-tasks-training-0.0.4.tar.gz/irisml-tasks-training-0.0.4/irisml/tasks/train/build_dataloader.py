import inspect
import typing
import torch.utils.data


class Dataset(torch.utils.data.Dataset):
    """Dataset wrapper to support both image-only transforms and image-and-targets transforms."""
    def __init__(self, dataset, transform):
        self._dataset = dataset
        self._transform = transform
        self._num_transform_args = self._get_num_args(transform)
        assert 1 <= self._num_transform_args <= 2

    def __len__(self):
        return len(self._dataset)

    def __getitem__(self, index):
        item = self._dataset[index]
        assert len(item) == 2
        if self._num_transform_args == 1:
            return self._transform(item[0]), item[1]
        elif self._num_transform_args == 2:
            return self._transform(*item)

    @staticmethod
    def _get_num_args(function):
        args = inspect.getfullargspec(function).args
        if args[0] == 'self':
            return len(args) - 1
        return len(args)


def collate(batch) -> typing.List:
    """Handle batching.

    Supported batch formats are:
        [(Tensor[C, H, W], int), ...]  # multiclass classification
        [(Tensor[C, H, W], [int, ...]), ...]  # multiclass or multilabel classification
        [(Tensor[C, H, W], Tensor[T]), ...]  # multiclass or multilabel classification
        [(Tensor[C, H, W], [[tag, x, y, x2, y2], ...]), ...]  # object detection
        [(Tensor[C, H, W], Tensor[T, 5]), ...]  # object detection
        [Tensor[C, H, W], ...]  # prediction
    """

    if isinstance(batch[0], tuple):
        return [_collate_tensor([b[0] for b in batch]), _collate_targets([b[1] for b in batch])]
    elif isinstance(batch[0], torch.Tensor):
        return [_collate_tensor(batch), None]

    raise TypeError(f"Unexpected type: {type(batch[0])}")


def _collate_tensor(batch: typing.List):
    """
    Inputs are:
        A list of Tensor[C, H, W] or
        A list of (Tensor[C, H, W], Tensor)
    """
    if isinstance(batch[0], torch.Tensor):
        if all(b.shape == (1,) for b in batch):
            return torch.cat(batch)

        if all(batch[0].shape == b.shape for b in batch):
            return torch.stack(batch, 0)

        return batch
    elif isinstance(batch[0], tuple):
        # For image-text dataset.
        return _collate_tensor([b[0] for b in batch]), _collate_tensor([b[1] for b in batch])

    raise TypeError(f"Unexpected type: {type(batch[0])}")


def _collate_targets(batch: typing.List):
    if isinstance(batch[0], torch.Tensor):
        return _collate_tensor(batch)

    if isinstance(batch[0], list):
        if any(b and isinstance(b[0], list) for b in batch):  # batch = [[[...], ...], ...]
            return [torch.tensor(b).reshape(-1, 5) for b in batch]
        elif any(b and isinstance(b[0], int) for b in batch):  # batch = [[int, ...], ...]
            return _collate_tensor([torch.tensor(b) for b in batch])
        elif not any(batch):
            return batch
    elif isinstance(batch[0], int):
        return torch.tensor(batch)


def build_dataloader(dataset, transform, batch_size: int, shuffle=True, drop_last=True):
    my_dataset = Dataset(dataset, transform)
    return torch.utils.data.DataLoader(my_dataset, batch_size=batch_size, num_workers=4, shuffle=shuffle, drop_last=drop_last, pin_memory=True, collate_fn=collate)
