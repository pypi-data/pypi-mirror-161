import collections
import dataclasses
import logging
import statistics
import typing
import sklearn.metrics
import torch
import torchvision.ops
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Calculate mean average precision for object detection task results.

    Note that this is a naive implementation. The evaluation results might be different from other libraries.

    Test-time augmentation is not considered.
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        predictions: typing.List[torch.Tensor]
        dataset: torch.utils.data.Dataset

    @dataclasses.dataclass
    class Config:
        iou_thresholds: typing.List[float] = dataclasses.field(default_factory=lambda: [0.5, 0.75, 0.9])

    @dataclasses.dataclass
    class Outputs:
        results: typing.List[float] = None

    class Evaluator:
        def __init__(self, predictions, targets):
            assert len(predictions) == len(targets)
            self._eval_predictions = collections.defaultdict(lambda: collections.defaultdict(list))
            self._eval_ground_truths = collections.defaultdict(lambda: collections.defaultdict(list))
            for img_index, prediction in enumerate(predictions):
                if len(prediction.shape) != 2 or prediction.shape[1] != 6:
                    logger.warning(f"Invalid prediction shape is detected. Ignoring... {prediction.shape}")
                    continue

                for b in prediction:
                    self._eval_predictions[int(b[0])][img_index].append(b[1:])

            for p in self._eval_predictions.values():
                for q in p.values():
                    q.sort(key=lambda x: -x[1])

            for img_index, target in enumerate(targets):
                if isinstance(target, list):
                    target = torch.tensor(target)

                if target.shape[0] == 0:  # Ignore examples with no bounding box.
                    continue

                if len(target.shape) != 2 or target.shape[1] != 5:
                    logger.warning(f"Invalid target shape is detected. Ignoring... {target.shape}")
                    continue

                for t in target:
                    self._eval_ground_truths[int(t[0])][img_index].append(t[1:])

        def calculate_average_precision(self, iou):
            class_ids = set(list(self._eval_predictions.keys()) + list(self._eval_ground_truths.keys()))
            if not class_ids:
                return 0.0

            average_precisions = []
            for c in class_ids:
                samples = []
                num_ground_truths = sum(len(x) for x in self._eval_ground_truths[c].values())
                for i in set(list(self._eval_predictions[c].keys()) + list(self._eval_ground_truths[c].keys())):
                    samples.extend(self._evaluate_boxes(self._eval_predictions[c][i], self._eval_ground_truths[c][i], iou))

                if num_ground_truths == 0 or not samples or not any(s[0] for s in samples):
                    average_precisions.append(0.0)
                    continue

                recall = float(sum(s[0] for s in samples)) / num_ground_truths
                average_precisions.append(sklearn.metrics.average_precision_score([x[0] for x in samples], [x[1] for x in samples]) * recall)
            return statistics.mean(average_precisions)

        @staticmethod
        def _evaluate_boxes(predictions, ground_truths, iou_threshold):
            """Check if each boxes are correct.

            Args:
                predictions: [[prob, x1, y1, x2, y2], ...]
                ground_truths: [[x1, y1, x2, y2], ...]
            Returns:
                [(is_correct, probs), ...]
            """
            if not ground_truths:
                return [(False, p[0]) for p in predictions]
            if not predictions:
                return []

            predictions = torch.stack(predictions)
            ground_truths = torch.stack(ground_truths)
            ious = torchvision.ops.box_iou(predictions[:, 1:], ground_truths)
            assert len(ious) == len(predictions)

            # predictions is already sorted by probability.
            results = []
            for i in range(len(ious)):
                best_iou, best_box = ious[i].max(dim=0)
                if best_iou >= iou_threshold:
                    ious[:, best_box] = -1
                    results.append((True, predictions[i][0]))
                else:
                    results.append((False, predictions[i][0]))
            return results

    def execute(self, inputs):
        targets = [x[1] for x in inputs.dataset]
        evaluator = Task.Evaluator(inputs.predictions, targets)
        results = [evaluator.calculate_average_precision(iou) for iou in self.config.iou_thresholds]
        logger.info(f"mAP: {results}")
        return self.Outputs(results)

    def dry_run(self, inputs):
        results = [0.0 for _ in self.config.iou_thresholds]
        return self.Outputs(results)
