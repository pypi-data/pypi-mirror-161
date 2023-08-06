try:

    from pytorch_lightning.utilities.logger import _convert_params  # noqa: F401
    from pytorch_lightning.utilities.logger import _sanitize_callable_params  # noqa: F401
    from pytorch_lightning.utilities.logger import _flatten_dict  # noqa: F401
    from pytorch_lightning.utilities.logger import _sanitize_params  # noqa: F401
    from pytorch_lightning.utilities.logger import _add_prefix  # noqa: F401
    from pytorch_lightning.utilities.logger import _name  # noqa: F401
    from pytorch_lightning.utilities.logger import _version  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
