try:

    from pytorch_lightning.loggers.wandb import _WANDB_AVAILABLE  # noqa: F401
    from pytorch_lightning.loggers.wandb import _WANDB_GREATER_EQUAL_0_10_22  # noqa: F401
    from pytorch_lightning.loggers.wandb import _WANDB_GREATER_EQUAL_0_12_10  # noqa: F401
    from pytorch_lightning.loggers.wandb import WandbLogger  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
