try:

    from pytorch_lightning.profilers.simple import log  # noqa: F401
    from pytorch_lightning.profilers.simple import _TABLE_ROW_EXTENDED  # noqa: F401
    from pytorch_lightning.profilers.simple import _TABLE_DATA_EXTENDED  # noqa: F401
    from pytorch_lightning.profilers.simple import _TABLE_ROW  # noqa: F401
    from pytorch_lightning.profilers.simple import _TABLE_DATA  # noqa: F401
    from pytorch_lightning.profilers.simple import SimpleProfiler  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
