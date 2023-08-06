import logging
import sys
import torch.distributed
import tqdm
from .plugin_base import PluginBase


class TqdmLoggingHandler(logging.StreamHandler):
    def emit(self, record):
        msg = self.format(record)
        tqdm.tqdm.write(msg, file=self.stream)
        self.flush()


def _is_console_handler(handler):
    return isinstance(handler, logging.StreamHandler) and handler.stream in (sys.stdout, sys.stderr)


class Plugin(PluginBase):
    def on_train_start(self, trainer, model):
        self._disabled = torch.distributed.is_initialized() and torch.distributed.get_rank() != 0
        if not self._disabled:
            self._training_progressbar = tqdm.tqdm(total=trainer.num_epochs, position=0, disable=None)
            # Replace the logging stream handlers
            self._original_handlers = logging.root.handlers
            stream_handlers = [h for h in logging.root.handlers if _is_console_handler(h)]
            if stream_handlers:
                tqdm_handler = TqdmLoggingHandler()
                tqdm_handler.setFormatter(stream_handlers[0].formatter)
                tqdm_handler.stream = stream_handlers[0].stream
                logging.root.handlers = [h for h in logging.root.handlers if not _is_console_handler(h)] + [tqdm_handler]

    def on_train_end(self, trainer, model):
        if not self._disabled:
            self._training_progressbar.close()
            logging.root.handlers = self._original_handlers

    def on_train_epoch_end(self, trainer, model, epoch_index):
        if not self._disabled:
            self._epoch_progressbar.close()
            self._training_progressbar.update(1)

    def on_train_epoch_start(self, trainer, model, epoch_index):
        if not self._disabled:
            self._epoch_progressbar = tqdm.tqdm(total=len(trainer.train_dataloader), position=1, leave=None, disable=None)

    def on_train_batch_end(self, trainer, model, loss, batch, batch_index):
        if not self._disabled:
            self._epoch_progressbar.update(1)
