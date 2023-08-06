try:

    from pytorch_lightning.demos.boring_classes import RandomDictDataset  # noqa: F401
    from pytorch_lightning.demos.boring_classes import RandomDataset  # noqa: F401
    from pytorch_lightning.demos.boring_classes import RandomIterableDataset  # noqa: F401
    from pytorch_lightning.demos.boring_classes import RandomIterableDatasetWithLen  # noqa: F401
    from pytorch_lightning.demos.boring_classes import BoringModel  # noqa: F401
    from pytorch_lightning.demos.boring_classes import BoringDataModule  # noqa: F401
    from pytorch_lightning.demos.boring_classes import ManualOptimBoringModel  # noqa: F401
    from pytorch_lightning.demos.boring_classes import DemoModel  # noqa: F401
    from pytorch_lightning.demos.boring_classes import Net  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
