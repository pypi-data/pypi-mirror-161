try:

    from pytorch_lightning.profiler.base import AbstractProfiler, BaseProfiler
    from pytorch_lightning.profilers.advanced import AdvancedProfiler
    from pytorch_lightning.profilers.base import PassThroughProfiler
    from pytorch_lightning.profilers.profiler import Profiler
    from pytorch_lightning.profilers.pytorch import PyTorchProfiler
    from pytorch_lightning.profilers.simple import SimpleProfiler
    from pytorch_lightning.profilers.xla import XLAProfiler

    from pytorch_lightning.profiler import __all__  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
