import copy
import dataclasses
import typing
import irisml.core
import torch


class Task(irisml.core.TaskBase):
    """Append a classifier model to a given model. A predictor and a loss module will be added, too.

    Inputs:
        model (torch.nn.Module): An encoder model
        classifier (torch.nn.Module): A classifier model. The input shape of this module must match with the outptu shape of the encoder model.
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        model: torch.nn.Module
        classifier: torch.nn.Module

    @dataclasses.dataclass
    class Config:
        task_type: typing.Literal['multiclass_classification', 'multilabel_classification']

    @dataclasses.dataclass
    class Outputs:
        model: torch.nn.Module = None

    def execute(self, inputs):
        model = ClassifierModel(copy.deepcopy(inputs.model), copy.deepcopy(inputs.classifier), self.config.task_type)
        return self.Outputs(model)


class ClassifierModel(torch.nn.Module):
    MODULES = {
        'multiclass_classification': (torch.nn.CrossEntropyLoss(), torch.nn.Softmax(1)),
        'multilabel_classification': (torch.nn.BCEWithLogitsLoss(), torch.nn.Sigmoid()),
    }

    def __init__(self, model, classifier, task_type):
        super().__init__()
        self._model = model
        self._classifier = classifier
        self._criterion, self._predictor = self.MODULES[task_type]

    def forward(self, *args):
        return self._classifier(self._model(*args))

    @property
    def criterion(self):
        return self._criterion

    @property
    def predictor(self):
        return self._predictor
