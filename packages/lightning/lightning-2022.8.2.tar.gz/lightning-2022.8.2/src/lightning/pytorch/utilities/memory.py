try:

    from pytorch_lightning.utilities.memory import recursive_detach  # noqa: F401
    from pytorch_lightning.utilities.memory import is_oom_error  # noqa: F401
    from pytorch_lightning.utilities.memory import is_cuda_out_of_memory  # noqa: F401
    from pytorch_lightning.utilities.memory import is_cudnn_snafu  # noqa: F401
    from pytorch_lightning.utilities.memory import is_out_of_cpu_memory  # noqa: F401
    from pytorch_lightning.utilities.memory import garbage_collection_cuda  # noqa: F401
    from pytorch_lightning.utilities.memory import get_gpu_memory_map  # noqa: F401
    from pytorch_lightning.utilities.memory import get_model_size_mb  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
