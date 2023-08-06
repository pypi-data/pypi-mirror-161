try:

    from pytorch_lightning.overrides.fairscale import _FAIRSCALE_AVAILABLE  # noqa: F401
    if _FAIRSCALE_AVAILABLE:
        from pytorch_lightning.overrides.fairscale import LightningShardedDataParallel  # noqa: F401
        from pytorch_lightning.overrides.fairscale import unwrap_lightning_module_sharded  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
