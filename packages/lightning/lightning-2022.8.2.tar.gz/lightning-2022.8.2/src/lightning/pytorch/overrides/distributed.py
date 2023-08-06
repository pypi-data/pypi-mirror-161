try:

    from pytorch_lightning.overrides.distributed import LightningDistributedModule  # noqa: F401
    from pytorch_lightning.overrides.distributed import _find_tensors  # noqa: F401
    from pytorch_lightning.overrides.distributed import prepare_for_backward  # noqa: F401
    from pytorch_lightning.overrides.distributed import UnrepeatedDistributedSampler  # noqa: F401
    from pytorch_lightning.overrides.distributed import _DatasetSamplerWrapper  # noqa: F401
    from pytorch_lightning.overrides.distributed import DistributedSamplerWrapper  # noqa: F401
    from pytorch_lightning.overrides.distributed import UnrepeatedDistributedSamplerWrapper  # noqa: F401
    from pytorch_lightning.overrides.distributed import IndexBatchSamplerWrapper  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
