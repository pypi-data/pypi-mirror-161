import unittest
import torch
from irisml.tasks.build_zero_shot_classifier import Task


class TestBuildZeroShotClassifier(unittest.TestCase):
    def test_simple(self):
        zero_feature = torch.ones(32)
        zero_feature[0] = 10
        one_feature = torch.ones(32)
        one_feature[1] = 10

        text_features = [one_feature, zero_feature, one_feature, zero_feature]
        text_classes = [1, 0, 1, 0]
        inputs = Task.Inputs(text_features, text_classes)
        outputs = Task(Task.Config(num_classes=2)).execute(inputs)

        self.assertEqual(torch.argmax(outputs.classifier(one_feature)), 1)
        self.assertEqual(torch.argmax(outputs.classifier(zero_feature)), 0)
