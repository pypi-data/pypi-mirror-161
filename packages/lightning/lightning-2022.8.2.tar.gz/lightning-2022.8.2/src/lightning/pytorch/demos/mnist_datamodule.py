try:

    from pytorch_lightning.demos.mnist_datamodule import _DATASETS_PATH  # noqa: F401
    from pytorch_lightning.demos.mnist_datamodule import _MNIST  # noqa: F401
    from pytorch_lightning.demos.mnist_datamodule import MNIST  # noqa: F401
    from pytorch_lightning.demos.mnist_datamodule import MNISTDataModule  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
