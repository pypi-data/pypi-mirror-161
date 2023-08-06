try:

    from pytorch_lightning.loops.optimization.closure import T  # noqa: F401
    from pytorch_lightning.loops.optimization.closure import OutputResult  # noqa: F401
    from pytorch_lightning.loops.optimization.closure import AbstractClosure  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
