try:

    from pytorch_lightning.utilities.fetching import _profile_nothing  # noqa: F401
    from pytorch_lightning.utilities.fetching import AbstractDataFetcher  # noqa: F401
    from pytorch_lightning.utilities.fetching import _no_op_batch_to_device  # noqa: F401
    from pytorch_lightning.utilities.fetching import DataFetcher  # noqa: F401
    from pytorch_lightning.utilities.fetching import InterBatchParallelDataFetcher  # noqa: F401
    from pytorch_lightning.utilities.fetching import StepFuncDataLoaderIter  # noqa: F401
    from pytorch_lightning.utilities.fetching import DataLoaderIterDataFetcher  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
