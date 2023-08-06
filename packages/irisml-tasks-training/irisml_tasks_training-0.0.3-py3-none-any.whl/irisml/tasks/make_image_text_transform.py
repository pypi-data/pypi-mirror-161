import dataclasses
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
        transform = ImageTextClassificationTransform(inputs.image_transform, inputs.class_names, inputs.prompt_generator, inputs.tokenizer)
        return self.Outputs(transform)

    def dry_run(self, inputs):
        return self.execute(inputs)


class ImageTextClassificationTransform(torch.nn.Module):
    def __init__(self, image_transform, class_names, prompt_generator, tokenizer):
        super().__init__()
        self._image_transform = image_transform
        self._class_names = class_names
        self._prompt_generator = prompt_generator
        self._tokenizer = tokenizer

    def forward(self, inputs, targets):
        image = inputs
        image, targets = self._image_transform(image, targets)
        prompts = self._prompt_generator(self._class_names[targets])
        text = self._tokenizer(random.choice(prompts))
        return (image, text), targets
