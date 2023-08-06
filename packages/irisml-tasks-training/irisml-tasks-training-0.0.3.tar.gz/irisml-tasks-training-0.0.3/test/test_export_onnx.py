import unittest
import torch
from irisml.core import Context
from irisml.tasks.export_onnx import Task


class TestExportOnnx(unittest.TestCase):
    def test_simple(self):
        class FakeModel(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self._model = torch.nn.Conv2d(3, 3, 3)

            @property
            def predictor(self):
                return torch.nn.Softmax(1)

            def forward(self, x):
                return self._model(x)

        model = FakeModel()

        task = Task(Task.Config(), Context())
        outputs = task.execute(Task.Inputs(model))
        self.assertIsNotNone(outputs)
