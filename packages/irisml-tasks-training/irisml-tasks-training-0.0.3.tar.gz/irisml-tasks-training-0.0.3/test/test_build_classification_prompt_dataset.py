import unittest
from irisml.tasks.build_classification_prompt_dataset import Task


class TestBuildClassificationPromptDataset(unittest.TestCase):
    def test_simple(self):
        class_names = ['class_a', 'class_b', 'class_c']

        def prompt_generator(x):
            return [f'A {x} A', f'B {x} B']

        inputs = Task.Inputs(class_names=class_names, prompt_generator=prompt_generator)
        outputs = Task(Task.Config()).execute(inputs)
        dataset = outputs.dataset

        data = [dataset[i] for i in range(len(dataset))]

        self.assertEqual(set(data), set([('A class_a A', 0), ('A class_b A', 1), ('A class_c A', 2), ('B class_a B', 0), ('B class_b B', 1), ('B class_c B', 2)]))
