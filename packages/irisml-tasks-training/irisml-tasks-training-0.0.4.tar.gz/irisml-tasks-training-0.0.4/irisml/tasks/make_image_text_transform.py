import dataclasses
import inspect
import random
import typing
import torch
import irisml.core


class Task(irisml.core.TaskBase):
    """Make a transform function for image-text classification.

    The transform function accepts (image (PIL.Image), targets (int)).

    Notes:
        This transform function depends on python's global random generator.

    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        image_transform: typing.Callable
        class_names: typing.List[str]
        prompt_generator: typing.Callable[[str], typing.List[str]]
        tokenizer: typing.Callable[[str], torch.Tensor]

    @dataclasses.dataclass
    class Outputs:
        transform: typing.Callable

    def execute(self, inputs):
        if not inputs.class_names:
            raise ValueError("Class names are required to make the transform function.")

        transform = ImageTextClassificationTransform(inputs.image_transform, inputs.class_names, inputs.prompt_generator, inputs.tokenizer)
        return self.Outputs(transform)

    def dry_run(self, inputs):
        return self.execute(inputs)


class ImageTextClassificationTransform:
    """A transform function for image-text classification.

    This function expects (inputs, targets) where inputs is a PIL Image object and targets is an int Tensor.
    For example, (PIL.Image.new(8, 8), torch.as_tensor(3))
    """
    def __init__(self, image_transform, class_names, prompt_generator, tokenizer):
        super().__init__()
        self._image_transform = image_transform
        self._num_transform_args = self._get_num_args(image_transform)
        self._class_names = class_names
        self._prompt_generator = prompt_generator
        self._tokenizer = tokenizer
        assert 1 <= self._num_transform_args <= 2

    def __call__(self, inputs, targets):
        image = inputs
        if self._num_transform_args == 1:
            image = self._image_transform(image)
        else:
            image, targets = self._image_transform(image, targets)
        prompts = self._prompt_generator(self._class_names[targets])
        text = self._tokenizer(random.choice(prompts))
        return (image, text), targets

    @staticmethod
    def _get_num_args(function):
        args = inspect.getfullargspec(function).args
        if args[0] == 'self':
            return len(args) - 1
        return len(args)
