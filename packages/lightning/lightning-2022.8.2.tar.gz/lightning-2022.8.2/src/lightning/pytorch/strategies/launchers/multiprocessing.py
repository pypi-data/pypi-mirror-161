try:

    from pytorch_lightning.strategies.launchers.multiprocessing import _MultiProcessingLauncher  # noqa: F401
    from pytorch_lightning.strategies.launchers.multiprocessing import _FakeQueue  # noqa: F401
    from pytorch_lightning.strategies.launchers.multiprocessing import _WorkerOutput  # noqa: F401
    from pytorch_lightning.strategies.launchers.multiprocessing import _GlobalStateSnapshot  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
