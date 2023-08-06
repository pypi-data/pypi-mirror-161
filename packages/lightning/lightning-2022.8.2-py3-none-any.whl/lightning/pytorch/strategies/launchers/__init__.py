try:

    from pytorch_lightning.strategies.launchers.base import _Launcher
    from pytorch_lightning.strategies.launchers.multiprocessing import _MultiProcessingLauncher
    from pytorch_lightning.strategies.launchers.subprocess_script import _SubprocessScriptLauncher
    from pytorch_lightning.strategies.launchers.xla import _XLALauncher

    from pytorch_lightning.strategies.launchers import __all__  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
