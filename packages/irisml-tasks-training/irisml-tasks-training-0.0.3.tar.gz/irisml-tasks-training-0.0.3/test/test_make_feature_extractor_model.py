import unittest
import torch
from irisml.tasks.make_feature_extractor_model import Task


class TestMakeFeatureExtractorModel(unittest.TestCase):
    def test_simple(self):
        class FakeModel(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.a = torch.nn.Conv2d(3, 3, 3)
                self.b = torch.nn.Conv2d(3, 3, 3)
                self.c = torch.nn.Conv2d(3, 3, 3)
                self.d = torch.nn.Sequential(self.a, self.b, self.c)  # Note that the self.a is used twice.

            def forward(self, x):
                a_out = self.a(x)
                return self.d(self.c(self.b(a_out))), a_out

        model = FakeModel()
        inputs = Task.Inputs(model)
        outputs = Task(Task.Config('a')).execute(inputs)

        input_tensor = torch.rand(1, 3, 27, 27)
        _, a_out = model(input_tensor)
        extracted = outputs.model.prediction_step(input_tensor)

        # If a module is used twice the first feature vector will be returned.
        self.assertTrue(torch.equal(a_out, extracted))

        # It supports nested module name.
        outputs = Task(Task.Config('d.0')).execute(inputs)
        extracted = outputs.model.prediction_step(input_tensor)
        self.assertTrue(torch.equal(a_out, extracted))
