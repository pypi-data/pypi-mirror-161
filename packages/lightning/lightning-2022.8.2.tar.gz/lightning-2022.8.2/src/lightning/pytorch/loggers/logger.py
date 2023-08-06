try:

    from pytorch_lightning.loggers.logger import rank_zero_experiment  # noqa: F401
    from pytorch_lightning.loggers.logger import Logger  # noqa: F401
    from pytorch_lightning.loggers.logger import LoggerCollection  # noqa: F401
    from pytorch_lightning.loggers.logger import DummyExperiment  # noqa: F401
    from pytorch_lightning.loggers.logger import DummyLogger  # noqa: F401
    from pytorch_lightning.loggers.logger import merge_dicts  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
