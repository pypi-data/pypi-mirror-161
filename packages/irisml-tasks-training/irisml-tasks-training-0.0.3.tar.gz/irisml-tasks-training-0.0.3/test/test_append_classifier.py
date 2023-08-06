import unittest
import torch
from irisml.tasks.append_classifier import Task


class TestAppendClassifier(unittest.TestCase):
    def test_simple(self):
        model = torch.nn.Sequential(torch.nn.Conv2d(3, 3, 3), torch.nn.Flatten())
        classifier = torch.nn.Linear(147, 5)
        inputs = Task.Inputs(model, classifier)
        outputs = Task(Task.Config('multiclass_classification')).execute(inputs)
        result = outputs.model(torch.rand(1, 3, 9, 9))
        self.assertIsNotNone(result)
        self.assertIsNotNone(outputs.model.criterion)
        self.assertIsNotNone(outputs.model.predictor)
