try:

    from pytorch_lightning.trainer.connectors.callback_connector import _log  # noqa: F401
    from pytorch_lightning.trainer.connectors.callback_connector import CallbackConnector  # noqa: F401
    from pytorch_lightning.trainer.connectors.callback_connector import _configure_external_callbacks  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
