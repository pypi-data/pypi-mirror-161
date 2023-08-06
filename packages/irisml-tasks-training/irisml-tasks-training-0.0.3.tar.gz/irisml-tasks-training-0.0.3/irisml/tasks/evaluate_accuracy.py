import dataclasses
import logging
import torch
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Calculate accuracy of the given prediction results.

    This task supports only multiclass classification.
    The dataset format is (<image(torch.Tensor)>, <target(int)>).
    The prediction results format is torch.Tensor[(N, num_classes)].
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        predictions: torch.Tensor
        dataset: torch.utils.data.Dataset

    @dataclasses.dataclass
    class Outputs:
        accuracy: float = 0

    def execute(self, inputs):
        if len(inputs.predictions.shape) != 2:
            raise RuntimeError(f"Invalid input shape: {inputs.predictions.shape}")

        num_samples = inputs.predictions.size(0)
        _, predicted_max_indexes = inputs.predictions.max(dim=1)
        targets = torch.Tensor([b[1] for b in inputs.dataset])

        if len(targets) != num_samples:
            raise RuntimeError(f"The number of prediction results and the number of targets doesn't match. {len(targets)} vs {num_samples}")

        accuracy = ((predicted_max_indexes == targets).sum() / num_samples).item()

        logger.info(f"Accuracy: {accuracy:.3f}")
        return self.Outputs(accuracy)
