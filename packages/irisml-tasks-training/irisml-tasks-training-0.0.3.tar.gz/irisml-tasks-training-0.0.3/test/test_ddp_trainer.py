import copy
import unittest
import torch
from irisml.tasks.train.ddp_trainer import DDPTrainer


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
    def criterion(self):
        return torch.nn.CrossEntropyLoss()


def fake_optimizer_factory(parameters):
    return torch.optim.SGD(parameters, lr=0.01)


def fake_lr_scheduler_factory(optimizer):
    return torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(optimizer, 1)


class TestDDPTrainer(unittest.TestCase):
    def test_train_without_dataload_thread(self):
        dataset = FakeDataset([[torch.rand(3, 256, 256), torch.tensor(1)], [torch.rand(3, 256, 256), torch.tensor(2)]])
        train_dataloader = torch.utils.data.DataLoader(dataset, num_workers=0)
        model = FakeModel()
        original_state_dict = copy.deepcopy(model.state_dict())
        trainer = DDPTrainer(model, fake_lr_scheduler_factory, fake_optimizer_factory, num_processes=4)
        trainer.train(train_dataloader, None, 1)

        # The training parameter is updated on this process.
        for key in original_state_dict:
            self.assertFalse(torch.equal(original_state_dict[key], trainer.model.state_dict()[key]))
