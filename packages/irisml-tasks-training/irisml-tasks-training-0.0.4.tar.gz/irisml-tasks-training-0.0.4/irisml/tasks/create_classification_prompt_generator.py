import dataclasses
import typing
import irisml.core


class Task(irisml.core.TaskBase):
    """Create a prompt generator for a classification task.

    Supported generator:
        'clip_imagenet_short': Generates prompts that are introduced in the openai/CLIP repository.
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Config:
        name: str = 'clip_imagenet_short'

    @dataclasses.dataclass
    class Outputs:
        generator: typing.Callable[[str], typing.List[str]]

    def execute(self, inputs):
        if self.config.name == 'clip_imagenet_short':
            gen = clip_imagenet_short_generator
        else:
            raise RuntimeError
        return self.Outputs(gen)

    def dry_run(self, inputs):
        return self.execute(inputs)


def clip_imagenet_short_generator(label_name: str) -> typing.List[str]:
    templates = ['itap of a {}.',
                 'a bad photo of the {}.',
                 'a origami {}.',
                 'a photo of the large {}.',
                 'a {} in a video game.',
                 'art of the {}.',
                 'a photo of the small {}.']
    return [t.format(label_name) for t in templates]
