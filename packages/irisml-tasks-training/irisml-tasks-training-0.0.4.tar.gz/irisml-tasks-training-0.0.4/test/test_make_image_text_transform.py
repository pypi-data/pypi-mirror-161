import unittest
from irisml.tasks.make_image_text_transform import Task


class TestMakeImageTextTransform(unittest.TestCase):
    def test_simple(self):
        def image_transform(x, y):
            return x, y

        def prompt_generator(x):
            return [f'A {x} A', f'B {x} B']

        def tokenizer(x):
            return f'token {x}'

        class_names = ['class_a', 'class_b']
        inputs = Task.Inputs(image_transform=image_transform, class_names=class_names, prompt_generator=prompt_generator, tokenizer=tokenizer)
        outputs = Task(Task.Config()).execute(inputs)

        self.assertIn(outputs.transform('image', 0), ((('image', 'token A class_a A'), 0), (('image', 'token B class_a B'), 0)))
        self.assertIn(outputs.transform('image', 0), ((('image', 'token A class_a A'), 0), (('image', 'token B class_a B'), 0)))
        self.assertIn(outputs.transform('image', 0), ((('image', 'token A class_a A'), 0), (('image', 'token B class_a B'), 0)))
        self.assertIn(outputs.transform('image', 1), ((('image', 'token A class_b A'), 1), (('image', 'token B class_b B'), 1)))
        self.assertIn(outputs.transform('image', 1), ((('image', 'token A class_b A'), 1), (('image', 'token B class_b B'), 1)))
        self.assertIn(outputs.transform('image', 1), ((('image', 'token A class_b A'), 1), (('image', 'token B class_b B'), 1)))
