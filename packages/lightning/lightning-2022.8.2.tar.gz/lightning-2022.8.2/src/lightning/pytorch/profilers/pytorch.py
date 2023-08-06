try:

    from pytorch_lightning.profilers.pytorch import log  # noqa: F401
    from pytorch_lightning.profilers.pytorch import warning_cache  # noqa: F401
    from pytorch_lightning.profilers.pytorch import _PROFILER  # noqa: F401
    from pytorch_lightning.profilers.pytorch import RegisterRecordFunction  # noqa: F401
    from pytorch_lightning.profilers.pytorch import ScheduleWrapper  # noqa: F401
    from pytorch_lightning.profilers.pytorch import PyTorchProfiler  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
