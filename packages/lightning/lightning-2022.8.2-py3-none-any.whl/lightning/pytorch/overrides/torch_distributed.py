try:

    from pytorch_lightning.overrides.torch_distributed import _pickler  # noqa: F401
    from pytorch_lightning.overrides.torch_distributed import _unpickler  # noqa: F401
    from pytorch_lightning.overrides.torch_distributed import logger  # noqa: F401
    from pytorch_lightning.overrides.torch_distributed import _TORCH_DISTRIBUTED_AVAILABLE  # noqa: F401
    # Taken from https://github.com/pytorch/pytorch/blob/3466c1b6901f06a563b8cbfa3c942fa50bda835b/torch/distributed/distributed_c10d.py#L267 # noqa: E501
    from pytorch_lightning.overrides.torch_distributed import _rank_not_in_group  # noqa: F401
    # Taken from https://github.com/pytorch/pytorch/blob/3466c1b6901f06a563b8cbfa3c942fa50bda835b/torch/distributed/distributed_c10d.py#L1551 # noqa: E501
    from pytorch_lightning.overrides.torch_distributed import _object_to_tensor  # noqa: F401
    # Taken from https://github.com/pytorch/pytorch/blob/3466c1b6901f06a563b8cbfa3c942fa50bda835b/torch/distributed/distributed_c10d.py#L1563 # noqa: E501
    from pytorch_lightning.overrides.torch_distributed import _tensor_to_object  # noqa: F401
    from pytorch_lightning.overrides.torch_distributed import _broadcast_object_list  # noqa: F401
    if not _TORCH_DISTRIBUTED_AVAILABLE:

        from pytorch_lightning.overrides.torch_distributed import _broadcast_noop  # noqa: F401
        from pytorch_lightning.overrides.torch_distributed import broadcast_object_list  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
