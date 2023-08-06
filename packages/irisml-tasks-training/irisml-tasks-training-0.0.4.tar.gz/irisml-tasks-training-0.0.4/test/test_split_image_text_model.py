import unittest
import torch.nn
from irisml.tasks.split_image_text_model import Task


class TestSplitImageTextModel(unittest.TestCase):
    def test_simple(self):
        class FakeModel(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.image_model = torch.nn.Conv2d(3, 3, 3)
                self.text_model = torch.nn.Conv2d(3, 3, 3)
                self.image_projection = torch.nn.Identity()
                self.text_projection = torch.nn.Identity()

        inputs = Task.Inputs(FakeModel())
        outputs = Task(Task.Config()).execute(inputs)
        self.assertIsNotNone(outputs.image_model)
        self.assertIsNotNone(outputs.text_model)
