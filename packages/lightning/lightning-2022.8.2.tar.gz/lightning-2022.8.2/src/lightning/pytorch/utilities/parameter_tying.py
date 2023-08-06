try:

    from pytorch_lightning.utilities.parameter_tying import find_shared_parameters  # noqa: F401
    from pytorch_lightning.utilities.parameter_tying import _find_shared_parameters  # noqa: F401
    from pytorch_lightning.utilities.parameter_tying import set_shared_parameters  # noqa: F401
    from pytorch_lightning.utilities.parameter_tying import _get_module_by_path  # noqa: F401
    from pytorch_lightning.utilities.parameter_tying import _set_module_by_path  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
