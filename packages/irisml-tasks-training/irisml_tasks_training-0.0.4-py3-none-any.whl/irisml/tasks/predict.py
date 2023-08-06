import dataclasses
import itertools
import logging
import math
import multiprocessing
import queue
import typing
import torch.nn
import torch.utils.data
import irisml.core
from irisml.tasks.train.build_dataloader import build_dataloader
from irisml.tasks.train.ddp_utils import spawn_processes, recreate_dataloader_with_new_sampler

logger = logging.getLogger(__name__)


class Predictor:
    def __init__(self, model, device=torch.device('cpu')):
        self._model = model
        self._device = device
        self._predictor = getattr(model, 'predictor', None)

    @property
    def device(self):
        return self._device

    @torch.no_grad()
    def predict(self, dataloader):
        self._model.to(self.device)

        was_training = self._model.training
        self._model.eval()

        results = []
        for batch_index, batch in enumerate(dataloader):
            batch_results = self.prediction_step(batch, batch_index)
            results.append(batch_results)

        if was_training:
            self._model.train()

        self._model.to(torch.device('cpu'))
        return self._move_to_cpu(self._aggregate_results(results))

    def prediction_step(self, batch, batch_index):
        inputs, targets = batch
        inputs = self._to_device(inputs)
        if hasattr(self._model, 'prediction_step'):
            batch_results = self._model.prediction_step(inputs)
        elif self._predictor is not None:
            outputs = self._model(inputs)
            batch_results = self._predictor(outputs)
        else:
            batch_results = self._model(inputs)
        return batch_results

    def _aggregate_results(self, results):
        if torch.is_tensor(results[0]):
            return torch.cat(results)
        elif isinstance(results[0], list):
            return list(itertools.chain(*results))
        else:
            raise RuntimeError(f"Unexpected result types: {results[0]}")

    def _to_device(self, data):
        if isinstance(data, list):
            return [self._to_device(d) for d in data]
        elif isinstance(data, tuple):
            return tuple(self._to_device(d) for d in data)
        elif hasattr(data, 'to'):
            return data.to(self.device, non_blocking=True)
        return data

    @staticmethod
    def _move_to_cpu(value):
        if torch.is_tensor(value):
            return value.to(torch.device('cpu'))
        elif isinstance(value, list):
            return [Predictor._move_to_cpu(x) for x in value]
        elif isinstance(value, (int, float, str)):
            return value
        else:
            raise ValueError(f"Unexpected value type: {type(value)}")


class SubsetSequentialSampler(torch.utils.data.Sampler):
    def __init__(self, data_source, start_index, end_index):
        self._start_index = start_index
        self._end_index = end_index
        assert start_index < end_index
        super().__init__(data_source)

    def __len__(self):
        return self._end_index - self._start_index

    def __iter__(self):
        return iter(range(self._start_index, self._end_index))


class DistributedPredictor(Predictor):
    def __init__(self, model, num_processes, device=torch.device('cpu')):
        self._num_processes = num_processes
        super().__init__(model, device)

    def predict(self, dataloader):
        mp_queue = multiprocessing.get_context('spawn').JoinableQueue(self._num_processes)
        num_examples_per_process = math.ceil(len(dataloader.dataset) / self._num_processes)
        context = spawn_processes(self._predict_on_new_process, args=(dataloader, num_examples_per_process, mp_queue), nprocs=self._num_processes)
        all_results = {}

        while len(all_results) < self._num_processes:
            try:
                index, results = mp_queue.get(timeout=5)
                assert index not in all_results
                all_results[index] = results
            except queue.Empty:
                if not all(p.is_alive() for p in context.processes):
                    context.join(1)
                    raise RuntimeError("Failed to collect prediction results from the child processes.")

        aggregated = self._aggregate_results([all_results[i] for i in range(self._num_processes)])

        for _ in range(self._num_processes):
            mp_queue.task_done()

        context.join(5)

        return aggregated

    def _predict_on_new_process(self, process_index, dataloader, num_examples_per_process, mp_queue):
        if self._device.type == 'cuda':
            self._device = torch.device('cuda', process_index)
        start_index = num_examples_per_process * process_index
        end_index = min(len(dataloader.dataset), start_index + num_examples_per_process)
        logger.info(f"Launched a process {process_index} on device {self._device} for batches [{start_index}, {end_index}].")
        sampler = SubsetSequentialSampler(dataloader.dataset, start_index, end_index)
        subset_dataloader = recreate_dataloader_with_new_sampler(dataloader, sampler)
        try:
            results = super().predict(subset_dataloader)
        except Exception as e:
            logger.exception(f"Exception happend while predicting. {e}")
            raise
        logger.info(f"Completed predictions on the process {process_index}. Returning {len(results)} results.")

        mp_queue.put((process_index, results))
        mp_queue.join()


class Task(irisml.core.TaskBase):
    """Predict using a given model.

    This class assumes that the model.predictor returns a Tensor or a list of results.
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        dataset: torch.utils.data.Dataset
        transform: torch.nn.Module
        model: torch.nn.Module

    @dataclasses.dataclass
    class Config:
        batch_size: int = 1
        device: typing.Optional[typing.Literal['cpu', 'cuda']] = None
        num_processes: int = 1

    @dataclasses.dataclass
    class Outputs:
        predictions: typing.List = dataclasses.field(default_factory=list)

    def execute(self, inputs):
        results = self._predict(inputs)
        return self.Outputs(results)

    def _predict(self, inputs):
        dataloader = build_dataloader(inputs.dataset, inputs.transform, batch_size=self.config.batch_size, shuffle=False, drop_last=False)
        predictor = Predictor(inputs.model, self._get_device()) if self.config.num_processes == 1 else DistributedPredictor(inputs.model, self.config.num_processes, self._get_device())
        results = predictor.predict(dataloader)
        if len(inputs.dataset) != len(results):
            raise RuntimeError(f"Couldn't get the expected number of prediction results. Expected: {len(inputs.dataset)}. Actual: {len(results)}")
        return results

    def _get_device(self) -> torch.device:
        """Get a torch device based on the configuration. If not specified explicitly, it uses cuda if available."""
        if self.config.device:
            device_name = self.config.device
        else:
            device_name = 'cuda' if torch.cuda.is_available() else 'cpu'
            logger.info(f"Training device is selected automatically: {device_name}. To specify the device manually, please set Config.device.")

        return torch.device(device_name)
