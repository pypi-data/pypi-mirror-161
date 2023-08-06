import unittest
import torch
from irisml.tasks.predict import Task, SubsetSequentialSampler


class FakeDataset(torch.utils.data.Dataset):
    def __init__(self, data):
        self._data = data

    def __getitem__(self, index):
        return self._data[index]

    def __len__(self):
        return len(self._data)


class FakeModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.model = torch.nn.Conv2d(3, 3, 3)

    def forward(self, x):
        return torch.flatten(torch.nn.AdaptiveAvgPool2d(1)(self.model(x)), start_dim=1)

    @property
    def predictor(self):
        return torch.nn.Softmax(1)


def fake_transform(x, y):
    return x, y


class TestPredict(unittest.TestCase):
    def test_single(self):
        dataset = FakeDataset([[torch.rand(3, 256, 256), torch.tensor(1)], [torch.rand(3, 256, 256), torch.tensor(2)]])
        model = FakeModel()

        self._assert_prediction(dataset, model, 1)
        self._assert_prediction(dataset, model, 2)
        self._assert_prediction(dataset, model, 3)

    def test_distributed(self):
        dataset = FakeDataset([[torch.rand(3, 8, 8), torch.tensor(1)] for _ in range(6)])
        model = FakeModel()

        self._assert_prediction(dataset, model, 2, 2)
        self._assert_prediction(dataset, model, 1, 3)
        self._assert_prediction(dataset, model, 5, 2)

    def test_error_in_distributed(self):
        dataset = FakeDataset([[torch.rand(3, 8, 8), torch.tensor(1)] for _ in range(6)])
        model = FakeModel()
        model.forward = None  # It will fail to run the model.

        with self.assertRaises(Exception):
            self._assert_prediction(dataset, model, 2, 2)

    def test_sampler(self):
        dataset = FakeDataset([[torch.rand(3, 8, 8), torch.tensor(1)] for _ in range(6)])
        sampler = SubsetSequentialSampler(dataset, 0, 2)
        self.assertEqual(len(sampler), 2)
        iterator = iter(sampler)
        self.assertEqual(next(iterator), 0)
        self.assertEqual(next(iterator), 1)
        with self.assertRaises(StopIteration):
            next(iterator)

    def _assert_prediction(self, dataset, model, batch_size, num_processes=1):
        inputs = Task.Inputs(dataset=dataset, transform=fake_transform, model=model)
        task = Task(Task.Config(batch_size=batch_size, num_processes=num_processes))
        outputs = task.execute(inputs)
        self.assertEqual(len(outputs.predictions), len(dataset))
