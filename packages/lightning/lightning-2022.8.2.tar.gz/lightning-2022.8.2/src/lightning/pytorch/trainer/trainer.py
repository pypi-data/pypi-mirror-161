try:

    from pytorch_lightning.trainer.trainer import log  # noqa: F401
    from pytorch_lightning.trainer.trainer import Trainer  # noqa: F401
    from pytorch_lightning.trainer.trainer import _evaluation_context  # noqa: F401
    from pytorch_lightning.trainer.trainer import _determine_batch_limits  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
