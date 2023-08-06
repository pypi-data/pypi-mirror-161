try:

    from pytorch_lightning.plugins.precision.deepspeed import _DEEPSPEED_AVAILABLE  # noqa: F401
    from pytorch_lightning.plugins.precision.deepspeed import warning_cache  # noqa: F401
    from pytorch_lightning.plugins.precision.deepspeed import DeepSpeedPrecisionPlugin  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
