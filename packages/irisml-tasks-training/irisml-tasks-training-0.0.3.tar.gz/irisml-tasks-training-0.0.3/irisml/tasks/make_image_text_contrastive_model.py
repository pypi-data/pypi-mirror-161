import dataclasses
import typing
import irisml.core
import torch.distributed
import torch.nn
from irisml.tasks.train.ddp_utils import all_gather


class Task(irisml.core.TaskBase):
    """Make a model for image-text contrastive training.

    Currently this task supports two losses:
        clip (default): The loss function from https://arxiv.org/abs/2103.00020
        unicl: The loss function from https://arxiv.org/abs/2204.03610
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        image_model: torch.nn.Module
        text_model: torch.nn.Module

    @dataclasses.dataclass
    class Config:
        loss: typing.Literal['clip', 'unicl'] = 'clip'

    @dataclasses.dataclass
    class Outputs:
        model: torch.nn.Module = None

    def execute(self, inputs):
        model = ImageTextContrastiveModel(inputs.image_model, inputs.text_model, self.config.loss)
        return self.Outputs(model)

    def dry_run(self, inputs):
        return self.execute(inputs)


class CLIPContrastiveCriterion(torch.nn.Module):
    def forward(self, features, targets):
        image_features, text_features, logit_scale = features
        logits = logit_scale * image_features @ text_features.t()
        image_loss = torch.nn.functional.cross_entropy(logits, targets)
        text_loss = torch.nn.functional.cross_entropy(logits.t(), targets)
        return (image_loss + text_loss) / 2.0


class UnifiedContrastiveCriterion(torch.nn.Module):
    def forward(self, features, targets):
        """
        Args: (image_features, text_features, logit_scal), targets
            image_features (torch.Tensor): Shape (N, feature_size)
            text_features (torch.Tensor): Shape (N, feature_size)
            logit_scale (torch.Tensor): A scalar
            targets (torch.Tensor): Shape (N, 1).
        """
        image_features, text_features, logit_scale = features
        logits = logit_scale * image_features @ text_features.t()
        targets = (targets.view(-1, 1) == targets.view(1, -1)).float()
        targets_sum = torch.sum(targets, dim=-1)  # For each sample, there is at least one positive targets.
        image_loss = torch.nn.functional.cross_entropy(logits, targets, reduction='sum')
        text_loss = torch.nn.functional.cross_entropy(logits.t(), targets, reduction='sum')
        return (image_loss + text_loss) / targets_sum / 2.0


class ImageTextContrastiveModel(torch.nn.Module):
    def __init__(self, image_model, text_model, loss_name, logit_scale=2.659260036932778):
        """
        Notes:
            math.log(1 / 0.07) = 2.659260036932778
        """
        super().__init__()

        # The task 'split_image_text_model' depends on these attributes.
        self.image_model = image_model
        self.text_model = text_model
        self.logit_scale = torch.nn.Parameter(torch.tensor(logit_scale))

        if loss_name == 'clip':
            self._criterion = CLIPContrastiveCriterion()
        elif loss_name == 'unicl':
            self._criterion = UnifiedContrastiveCriterion()
        else:
            raise RuntimeError

    def forward(self, inputs):
        image_features = self.image_model(inputs[0])
        text_features = self.text_model(inputs[1])
        if torch.distributed.is_initialized():
            image_features = all_gather(image_features)
            text_features = all_gather(text_features)
        return image_features, text_features, self.logit_scale.exp()

    @property
    def criterion(self):
        return self._criterion

    def prediction_step(self, inputs):
        raise RuntimeError("Prediction is not supported. If you would like to try zero-shot classificaiton, see the task 'build_zero_shot_classifier'.")
