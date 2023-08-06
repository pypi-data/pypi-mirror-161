try:
    from pytorch_lightning.strategies.bagua import _BAGUA_AVAILABLE  # noqa: F401
    if _BAGUA_AVAILABLE:
        from pytorch_lightning.strategies.bagua import _bagua_reduce_ops  # noqa: F401
    from pytorch_lightning.strategies.bagua import log  # noqa: F401
    from pytorch_lightning.strategies.bagua import LightningBaguaModule  # noqa: F401
    from pytorch_lightning.strategies.bagua import BaguaStrategy  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
