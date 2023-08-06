import collections
import dataclasses
import logging
import typing
import torch
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Create a zero-shot classification layer."""
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        text_features: typing.List[torch.Tensor]
        text_classes: typing.List[int]

    @dataclasses.dataclass
    class Config:
        num_classes: int

    @dataclasses.dataclass
    class Outputs:
        classifier: torch.nn.Module = None

    def execute(self, inputs):
        num_examples = len(inputs.text_features)
        if len(inputs.text_classes) != num_examples:
            raise RuntimeError(f"The number of examples doesn't match. features={num_examples}, classes={len(inputs.text_classes)}")

        if max(inputs.text_classes) >= self.config.num_classes:
            raise RuntimeError(f"The max class index is higher than {self.config.num_classes}: {max(inputs.text_classes)}")
        feature_shape = inputs.text_features[0].shape
        logger.debug(f"Feature shape is {feature_shape}")

        features_per_class = collections.defaultdict(list)
        for c, f in zip(inputs.text_classes, inputs.text_features):
            features_per_class[c].append(f)

        embeddings_per_class = {}
        for c in features_per_class:
            class_embeddings = torch.stack(features_per_class[c])
            class_embeddings /= class_embeddings.norm(dim=-1, keepdim=True)
            class_embedding = class_embeddings.mean(dim=0)
            class_embedding /= class_embedding.norm()
            embeddings_per_class[c] = class_embedding
        weights_list = [embeddings_per_class[i] if i in embeddings_per_class else torch.zeros(*feature_shape) for i in range(self.config.num_classes)]
        weights = torch.stack(weights_list, dim=1).transpose(0, 1)  # TODO: Multiply with logit_scale?

        with torch.no_grad():
            classifier = torch.nn.Linear(weights.shape[1], weights.shape[0], bias=False)
            classifier.weight.copy_(weights)
        return self.Outputs(classifier)
