try:

    from pytorch_lightning.tuner.lr_finder import _MATPLOTLIB_AVAILABLE  # noqa: F401
    from pytorch_lightning.tuner.lr_finder import log  # noqa: F401
    from pytorch_lightning.tuner.lr_finder import _determine_lr_attr_name  # noqa: F401
    from pytorch_lightning.tuner.lr_finder import _LRFinder  # noqa: F401
    from pytorch_lightning.tuner.lr_finder import lr_find  # noqa: F401
    from pytorch_lightning.tuner.lr_finder import _LRCallback  # noqa: F401
    from pytorch_lightning.tuner.lr_finder import _LinearLR  # noqa: F401
    from pytorch_lightning.tuner.lr_finder import _ExponentialLR  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
