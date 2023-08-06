import copy
import dataclasses
import torch.nn
import irisml.core


class Task(irisml.core.TaskBase):
    """Split a image-text model into an image model and a text model.

    Inputs:
        model (torch.nn.Module): An input model. It must have 'image_model' and 'text_model' attributes.
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        model: torch.nn.Module

    @dataclasses.dataclass
    class Outputs:
        image_model: torch.nn.Module = None
        text_model: torch.nn.Module = None

    def execute(self, inputs):
        image_model = torch.nn.Sequential(copy.deepcopy(inputs.model.image_model), copy.deepcopy(inputs.model.image_projection))
        text_model = torch.nn.Sequential(copy.deepcopy(inputs.model.text_model), copy.deepcopy(inputs.model.text_projection))
        return self.Outputs(image_model, text_model)

    def dry_run(self, inputs):
        return self.execute(inputs)
