import logging
import time
import torch.cuda
from .plugin_base import PluginBase

logger = logging.getLogger(__name__)


class Plugin(PluginBase):
    def on_train_epoch_start(self, trainer, model, epoch_index):
        self._epoch_sum_loss = 0
        self._epoch_num_samples = 0
        self._num_iters = 0
        self._epoch_start = time.time()

    def on_train_epoch_end(self, trainer, model, epoch_index):
        loss = self._epoch_sum_loss / self._epoch_num_samples
        training_time = time.time() - self._epoch_start
        log = f"Epoch {epoch_index}: Training loss: {loss:.4f}, time: {training_time:.2f}s, iteration: {self._num_iters}"
        if trainer.device.type == 'cuda':
            total_memory = torch.cuda.get_device_properties(trainer.device).total_memory // (1024 * 1024)
            max_allocated = torch.cuda.max_memory_allocated(trainer.device) // (1024 * 1024)
            torch.cuda.reset_peak_memory_stats(trainer.device)
            log += f", CUDA max memory: {max_allocated}/{total_memory} MB"
        logger.info(log)

    def on_train_batch_end(self, trainer, model, loss, batch, batch_index):
        self._epoch_sum_loss += float(loss.item()) * len(batch[0])
        self._epoch_num_samples += len(batch[0])
        self._num_iters += 1
        return loss

    def on_validation_start(self, trainer, model):
        self._validation_sum_loss = 0
        self._validation_num_samples = 0
        self._validation_num_iters = 0

    def on_validation_batch_end(self, trainer, model, loss, batch, batch_index):
        self._validation_sum_loss += float(loss.item()) * len(batch[0])
        self._validation_num_samples += len(batch[0])
        self._validation_num_iters += 1

    def on_validation_end(self, trainer, model):
        loss = self._validation_sum_loss / self._validation_num_samples
        logger.info(f"Validation loss: {loss:.4f}, iteration: {self._validation_num_iters}")
