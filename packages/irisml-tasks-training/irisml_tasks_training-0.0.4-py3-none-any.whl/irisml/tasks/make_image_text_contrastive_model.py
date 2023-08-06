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
        image_feature_dim: typing.Optional[int] = None
        text_feature_dim: typing.Optional[int] = None
        projection_dim: typing.Optional[int] = 512

    @dataclasses.dataclass
    class Outputs:
        model: torch.nn.Module = None

    def execute(self, inputs):
        image_projection = torch.nn.Linear(self.config.image_feature_dim, self.config.projection_dim) if self.config.image_feature_dim and self.config.projection_dim else None
        text_projection = torch.nn.Linear(self.config.text_feature_dim, self.config.projection_dim) if self.config.text_feature_dim and self.config.projection_dim else None
        model = ImageTextContrastiveModel(inputs.image_model, inputs.text_model, image_projection, text_projection, self.config.loss)
        return self.Outputs(model)

    def dry_run(self, inputs):
        return self.execute(inputs)


class CLIPContrastiveCriterion(torch.nn.Module):
    def forward(self, features, targets):
        image_features, text_features, logit_scale = features
        logits = logit_scale * image_features @ text_features.t()
        image_loss = torch.nn.functional.cross_entropy(logits, torch.arange(len(logits), device=logits.device))
        text_loss = torch.nn.functional.cross_entropy(logits.t(), torch.arange(len(logits), device=logits.device))
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
    def __init__(self, image_model, text_model, image_projection, text_projection, loss_name, logit_scale=2.659260036932778):
        """
        Args:
            image_model (torch.nn.Module): input: Tensor[N, C, H, W], output: Tensor[N, F]
            text_model (torch.nn.Module): input: Tensor[N, T], output: Tensor[N, F2]
            image_projection (torch.nn.Module): Applied to image_model's output. Optional.
            text_projection (torch.nn.Module): Applied to text_model's output. Optional.
            loss_name: clip or unicl
        Notes:
            math.log(1 / 0.07) = 2.659260036932778
        """
        super().__init__()

        # The task 'split_image_text_model' depends on these attributes.
        self.image_model = image_model
        self.text_model = text_model
        self.image_projection = image_projection or torch.nn.Identity()
        self.text_projection = text_projection or torch.nn.Identity()
        self.logit_scale = torch.nn.Parameter(torch.tensor(logit_scale))

        if loss_name == 'clip':
            self._criterion = CLIPContrastiveCriterion()
        elif loss_name == 'unicl':
            self._criterion = UnifiedContrastiveCriterion()
        else:
            raise RuntimeError

    def forward(self, inputs):
        image_features = self.image_projection(self.image_model(inputs[0]))
        text_features = self.text_projection(self.text_model(inputs[1]))

        image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)
        text_features = text_features / text_features.norm(p=2, dim=-1, keepdim=True)

        return image_features, text_features, self.logit_scale.exp()

    def training_step(self, inputs, targets):
        image_features, text_features, logit_scale = self(inputs)
        if torch.distributed.is_initialized():
            image_features = all_gather(image_features)
            text_features = all_gather(text_features)

        assert len(image_features.shape) == 2 and len(text_features.shape) == 2 and image_features.shape == text_features.shape
        loss = self._criterion((image_features, text_features, logit_scale), targets)
        return {'loss': loss}

    def prediction_step(self, inputs):
        raise RuntimeError("Prediction is not supported. If you would like to try zero-shot classificaiton, see the task 'build_zero_shot_classifier'.")
