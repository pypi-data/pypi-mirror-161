import dataclasses
import torch


@dataclasses.dataclass
class LrSchedulerConfig:
    name: str = 'cosine_annealing'


def build_lr_scheduler(config, optimizer, num_epochs):
    config = config or LrSchedulerConfig()

    if config.name == 'cosine_annealing':
        return torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(optimizer, num_epochs)
    elif config.name == 'linear_decreasing':
        return torch.optim.lr_scheduler.LinearLR(optimizer, start_factor=1, end_factor=0, total_iters=num_epochs)

    raise ValueError(f"Unsupported lr scheduler name: {config.name}")


class LrSchedulerFactory:
    def __init__(self, config: LrSchedulerConfig, num_epochs: int):
        self._config = config
        self._num_epochs = num_epochs

    def __call__(self, optimizer):
        return build_lr_scheduler(self._config, optimizer, self._num_epochs)
