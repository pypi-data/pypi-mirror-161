import datetime
import torch.utils.tensorboard
from .plugin_base import PluginBase


class Plugin(PluginBase):
    def on_train_start(self, trainer, model):
        current_time = datetime.datetime.now().strftime('%m%d%H%M%S')
        self._writer = torch.utils.tensorboard.SummaryWriter(f'logs/{current_time}')
        self._counter = 0

    def on_train_end(self, trainer, model):
        self._writer.close()

    def on_train_batch_end(self, trainer, model, loss, batch, batch_index):
        for i, lr in enumerate(g['lr'] for g in trainer.optimizer.param_groups):
            self._add_scalar(f'Lr{i}', lr, False)
        self._add_scalar('Loss/train', float(loss.item()))

    def on_validation_batch_end(self, trainer, model, loss, batch, batch_index):
        self._add_scalar('Loss/validation', float(loss.item()))

    def _add_scalar(self, name, value, increment=True):
        self._writer.add_scalar(name, value, self._counter)
        if increment:
            self._counter += 1
