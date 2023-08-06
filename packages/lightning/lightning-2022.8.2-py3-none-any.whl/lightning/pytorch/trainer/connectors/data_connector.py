try:

    from pytorch_lightning.trainer.connectors.data_connector import warning_cache  # noqa: F401
    from pytorch_lightning.trainer.connectors.data_connector import DataConnector  # noqa: F401
    from pytorch_lightning.trainer.connectors.data_connector import _DataLoaderSource  # noqa: F401
    from pytorch_lightning.trainer.connectors.data_connector import _DataHookSelector  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
