try:

    from pytorch_lightning.loggers.neptune import __all__  # noqa: F401
    from pytorch_lightning.loggers.neptune import _NEPTUNE_AVAILABLE  # noqa: F401
    from pytorch_lightning.loggers.neptune import _NEPTUNE_GREATER_EQUAL_0_9  # noqa: F401
    from pytorch_lightning.loggers.neptune import log  # noqa: F401
    from pytorch_lightning.loggers.neptune import _INTEGRATION_VERSION_KEY  # noqa: F401
    from pytorch_lightning.loggers.neptune import _LEGACY_NEPTUNE_INIT_KWARGS  # noqa: F401
    from pytorch_lightning.loggers.neptune import _LEGACY_NEPTUNE_LOGGER_KWARGS  # noqa: F401
    from pytorch_lightning.loggers.neptune import NeptuneLogger  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
