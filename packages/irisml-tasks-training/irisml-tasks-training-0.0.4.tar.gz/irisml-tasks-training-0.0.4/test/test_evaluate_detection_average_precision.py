import unittest
import torch
from irisml.tasks.evaluate_detection_average_precision import Task


class TestEvaluateDetectionAveragePrecision(unittest.TestCase):
    def test_evaluate(self):
        task = Task(Task.Config([0.5, 0.75, 0.9]))

        inputs = Task.Inputs(predictions=[torch.Tensor([[0, 0.5, 0, 0, 1, 1]])], dataset=[(None, torch.tensor([[0, 0, 0, 1, 1]]))])
        results = task.execute(inputs)
        self.assertEqual(results.results, [1.0, 1.0, 1.0])

        inputs = Task.Inputs(predictions=[torch.Tensor([[0, 0.5, 0.9, 0.9, 1, 1]])], dataset=[(None, torch.tensor([[0, 0, 0, 0.1, 0.1]]))])
        results = task.execute(inputs)
        self.assertEqual(results.results, [0.0, 0.0, 0.0])
