class PluginBase:
    def on_train_start(self, trainer, model):
        pass

    def on_train_end(self, trainer, model):
        pass

    def on_train_epoch_start(self, trainer, model, epoch_index):
        pass

    def on_train_epoch_end(self, trainer, model, epoch_index):
        pass

    def on_train_batch_start(self, trainer, model, batch, batch_index):
        return batch

    def on_train_batch_end(self, trainer, model, loss, batch, batch_index):
        pass

    def on_train_backward_start(self, trainer, model, loss):
        return loss

    def on_validation_start(self, trainer, model):
        pass

    def on_validation_end(self, trainer, model):
        pass

    def on_validation_batch_start(self, trainer, model, batch, batch_index):
        return batch

    def on_validation_batch_end(self, trainer, model, loss, batch, batch_index):
        pass
