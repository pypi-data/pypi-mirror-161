import unittest
from irisml.tasks.create_classification_prompt_generator import Task


class TestCreateClassificationPromptGenerator(unittest.TestCase):
    def test_simple(self):
        outputs = Task(Task.Config()).execute(Task.Inputs())

        results = outputs.generator('random_string')
        self.assertGreater(len(results), 1)
        self.assertTrue(all('random_string' in r for r in results))
