from .plugin_base import PluginBase


class Plugin(PluginBase):
    def on_train_epoch_start(self, trainer, model, epoch_index):
        # Reset the random seed for DistributedSampler so that it can sample differently at each epoch.
        trainer.train_dataloader.sampler.set_epoch(epoch_index)
