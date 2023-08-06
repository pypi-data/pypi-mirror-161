try:

    from pytorch_lightning.loggers.mlflow import log  # noqa: F401
    from pytorch_lightning.loggers.mlflow import LOCAL_FILE_URI_PREFIX  # noqa: F401
    from pytorch_lightning.loggers.mlflow import _MLFLOW_AVAILABLE  # noqa: F401
    from pytorch_lightning.loggers.mlflow import MLFlowLogger  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
