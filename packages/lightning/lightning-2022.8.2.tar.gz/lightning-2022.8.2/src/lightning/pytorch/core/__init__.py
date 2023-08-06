try:

    from pytorch_lightning.core.datamodule import LightningDataModule
    from pytorch_lightning.core.module import LightningModule

    from pytorch_lightning.core import __all__  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
