import contextlib
import logging
import multiprocessing
import os
import socket
import torch.multiprocessing
import torch.utils.data


def recreate_dataloader_with_distributed_sampler(dataloader: torch.utils.data.DataLoader):
    if isinstance(dataloader.sampler, torch.utils.data.RandomSampler):
        shuffle = True
    elif isinstance(dataloader.sampler, torch.utils.data.SequentialSampler):
        shuffle = False
    else:
        raise RuntimeError(f"DDP Trainer doesn't support the sampler {dataloader.sampler}. Please make a pull request.")

    # Create a new sampler. If shuffle is True, the default random seed 0 will be used.
    sampler = torch.utils.data.distributed.DistributedSampler(dataloader.dataset, shuffle=shuffle)
    return recreate_dataloader_with_new_sampler(dataloader, sampler)


def recreate_dataloader_with_new_sampler(dataloader: torch.utils.data.DataLoader, sampler: torch.utils.data.Sampler):
    return torch.utils.data.DataLoader(dataloader.dataset, dataloader.batch_size, sampler=sampler, num_workers=dataloader.num_workers,
                                       collate_fn=dataloader.collate_fn, pin_memory=dataloader.pin_memory, drop_last=dataloader.drop_last, timeout=dataloader.timeout,
                                       worker_init_fn=dataloader.worker_init_fn, prefetch_factor=dataloader.prefetch_factor)


def _get_available_port():
    """Find an available port number on the localhost."""
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def _wrap_function(process_index, target_function, args, logger_info):
    logging.getLogger().setLevel(logger_info[0])
    logging.getLogger('irisml').setLevel(logger_info[1])
    for h in logger_info[2]:
        logging.getLogger().addHandler(h)

    target_function(process_index, *args)


def spawn_processes(target_function, args, nprocs):
    """Spawn subprocesses and wait until one of them ends.

    The subprocess inherits logging handlers from the current process.

    Returns:
        SpawnContext
    """
    # Keep using the logger if it can be serialized and deserialized in the child process.
    # The Irisml's official log handlers are serializable, but sometimes other platform such as pytest might add a new log handler.
    pickleable_log_handlers = [h for h in logging.getLogger().handlers if hasattr(h, '__getstate__')]
    logger_info = (logging.getLogger().getEffectiveLevel(), logging.getLogger('irisml').getEffectiveLevel(), pickleable_log_handlers)

    # There is a bug in file_descriptor sharing that results in "bad value(s) in fds_to_keep" exception.
    # https://github.com/pytorch/pytorch/issues/31571
    torch.multiprocessing.set_sharing_strategy('file_system')

    # Set environment variables if they are not defined. AML can set those variables if DistributedConfig was used.
    if not os.getenv('MASTER_ADDR'):
        os.environ['MASTER_ADDR'] = 'localhost'
    if not os.getenv('MASTER_PORT'):
        os.environ['MASTER_PORT'] = str(_get_available_port())

    # This method will block until all processes end or any process fails.
    return torch.multiprocessing.spawn(_wrap_function, args=(target_function, args, logger_info), nprocs=nprocs, join=False)


def spawn_and_wait(target_function, args, nprocs):
    context = spawn_processes(target_function, args, nprocs)
    sentinels = [p.sentinel for p in context.processes]

    # Wait until one of the processes is terminated.
    multiprocessing.connection.wait(sentinels)

    return context


def all_gather(tensor):
    if not torch.distributed.is_initialized():
        raise RuntimeError("Distributed training is not initialized.")

    world_size = torch.distributed.get_world_size()
    rank = torch.distributed.get_rank()
    tensors = [torch.zeros_like(tensor) for _ in range(world_size)]
    torch.distributed.all_gather(tensors, tensor)

    tensors[rank] = tensor  # Make sure the local tensor keeps the gradients.
    return torch.cat(tensors, dim=0)
