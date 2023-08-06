try:

    from pytorch_lightning.utilities.argparse import _T  # noqa: F401
    from pytorch_lightning.utilities.argparse import ParseArgparserDataType  # noqa: F401
    from pytorch_lightning.utilities.argparse import from_argparse_args  # noqa: F401
    from pytorch_lightning.utilities.argparse import parse_argparser  # noqa: F401
    from pytorch_lightning.utilities.argparse import parse_env_variables  # noqa: F401
    from pytorch_lightning.utilities.argparse import get_init_arguments_and_types  # noqa: F401
    from pytorch_lightning.utilities.argparse import _get_abbrev_qualified_cls_name  # noqa: F401
    from pytorch_lightning.utilities.argparse import add_argparse_args  # noqa: F401
    from pytorch_lightning.utilities.argparse import _parse_args_from_docstring  # noqa: F401
    from pytorch_lightning.utilities.argparse import _gpus_allowed_type  # noqa: F401
    from pytorch_lightning.utilities.argparse import _int_or_float_type  # noqa: F401
    from pytorch_lightning.utilities.argparse import _precision_allowed_type  # noqa: F401
    from pytorch_lightning.utilities.argparse import _defaults_from_env_vars  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
