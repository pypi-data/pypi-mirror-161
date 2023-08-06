try:

    from pytorch_lightning.trainer.supporters import TensorRunningAccum  # noqa: F401
    from pytorch_lightning.trainer.supporters import SharedCycleIteratorState  # noqa: F401
    from pytorch_lightning.trainer.supporters import CycleIterator  # noqa: F401
    from pytorch_lightning.trainer.supporters import CombinedDataset  # noqa: F401
    from pytorch_lightning.trainer.supporters import CombinedLoader  # noqa: F401
    from pytorch_lightning.trainer.supporters import CombinedLoaderIterator  # noqa: F401
    from pytorch_lightning.trainer.supporters import _nested_calc_num_data  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
