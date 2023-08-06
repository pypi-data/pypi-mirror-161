try:

    from pytorch_lightning.accelerators.cuda import _log  # noqa: F401
    from pytorch_lightning.accelerators.cuda import CUDAAccelerator  # noqa: F401
    from pytorch_lightning.accelerators.cuda import get_nvidia_gpu_stats  # noqa: F401
    from pytorch_lightning.accelerators.cuda import _get_gpu_id  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
