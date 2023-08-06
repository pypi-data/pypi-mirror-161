import copy
import dataclasses
import functools
import typing
import torch
import irisml.core


class Task(irisml.core.TaskBase):
    """Make a wrapper model to extract a feature vector from a vision model.

    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        model: torch.nn.Module

    @dataclasses.dataclass
    class Config:
        output_module_name: typing.Optional[str] = None

    @dataclasses.dataclass
    class Outputs:
        model: torch.nn.Module = None

    def execute(self, inputs):
        model = FeatureExtractor(copy.deepcopy(inputs.model), self.config.output_module_name)
        return self.Outputs(model)

    def dry_run(self, inputs):
        return self.execute(inputs)


class FeatureExtractor(torch.nn.Module):
    def __init__(self, model, output_module_name=None):
        """Extract a feature vector from a model.

        Notes:
            - This class doesn't support multi-thread inference.
            - If the output module was used twice, the first feature vector will be returned.

        Args:
            model (torch.nn.Module): A model. Must not be re-used in other place.
            output_module_name: The name of the module to extract feature vectors.
        """
        super().__init__()
        self._model = model
        self._output_module_name = output_module_name

        if output_module_name:
            module = self._find_module(self._model, output_module_name)
            # Instead of having a plugin to remove the hook, we forget about it. The model shouldn't be reused.
            module.register_forward_hook(self._save_outputs)

    def prediction_step(self, inputs):
        self._features = None
        outputs = self._model(inputs)
        outputs = self._features if self._output_module_name else outputs
        self._features = None
        return outputs

    def _save_outputs(self, module, inputs, outputs):
        if self._features is None:
            self._features = copy.deepcopy(outputs.detach())

    @staticmethod
    def _find_module(model, name):
        names = name.split('.')
        return functools.reduce(getattr, names, model)
