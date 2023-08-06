import unittest
import torch
from irisml.tasks.get_targets_from_dataset import Task


class TestGetTargetsFromDataset(unittest.TestCase):
    def test_simple(self):
        class FakeDataset(torch.utils.data.Dataset):
            def __init__(self, data):
                super().__init__()
                self._data = data

            def __len__(self):
                return len(self._data)

            def __getitem__(self, index):
                return self._data[index]

        data = [('image0', 0), ('image1', 2), ('image2', 4)]
        inputs = Task.Inputs(FakeDataset(data))
        outputs = Task(Task.Config()).execute(inputs)

        targets = outputs.targets

        self.assertIsInstance(targets, torch.Tensor)
        self.assertEqual(targets.tolist(), [0, 2, 4])
