import dataclasses
import logging
import typing
import torch.utils.data
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Create a classification prompt dataset."""
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        class_names: typing.List[str]
        prompt_generator: typing.Callable[[str], typing.List[str]]

    @dataclasses.dataclass
    class Outputs:
        dataset: torch.utils.data.Dataset = None

    def execute(self, inputs):
        text_lists = [(t, i) for i, label in enumerate(inputs.class_names) for t in inputs.prompt_generator(label)]
        logger.debug(f"Created a text dataset. The number of examples: {len(text_lists)}. The number of classes: {len(inputs.class_names)}")
        return self.Outputs(TextListDataset(text_lists))

    def dry_run(self, inputs):
        return self.execute(inputs)


class TextListDataset(torch.utils.data.Dataset):
    def __init__(self, text_list: typing.List[typing.Tuple[str, int]]):
        self._data = text_list

    def __len__(self):
        return len(self._data)

    def __getitem__(self, index):
        return self._data[index]
