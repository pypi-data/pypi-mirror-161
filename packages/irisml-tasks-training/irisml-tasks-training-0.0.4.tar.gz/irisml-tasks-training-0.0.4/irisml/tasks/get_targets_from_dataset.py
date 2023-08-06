import dataclasses
import typing
import torch
import irisml.core


class Task(irisml.core.TaskBase):
    """Extract only targets from a given Dataset.

    If the targets are integers or tensors with same shape, a tensor will be returned. Otherwise, returns a list of targets.
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        dataset: torch.utils.data.Dataset

    @dataclasses.dataclass
    class Outputs:
        targets: typing.Union[typing.List, torch.Tensor] = dataclasses.field(default_factory=list)

    def execute(self, inputs):
        targets = [t for _, t in inputs.dataset]
        if torch.is_tensor(targets[0]):
            shape = targets[0].shape
            if all(t.shape == shape for t in targets):
                targets = torch.stack(targets)
        elif isinstance(targets[0], int):
            targets = torch.tensor(targets)

        return self.Outputs(targets)
