try:

    from pytorch_lightning.utilities.parsing import str_to_bool_or_str  # noqa: F401
    from pytorch_lightning.utilities.parsing import str_to_bool  # noqa: F401
    from pytorch_lightning.utilities.parsing import str_to_bool_or_int  # noqa: F401
    from pytorch_lightning.utilities.parsing import is_picklable  # noqa: F401
    from pytorch_lightning.utilities.parsing import clean_namespace  # noqa: F401
    from pytorch_lightning.utilities.parsing import parse_class_init_keys  # noqa: F401
    from pytorch_lightning.utilities.parsing import get_init_args  # noqa: F401
    from pytorch_lightning.utilities.parsing import collect_init_args  # noqa: F401
    from pytorch_lightning.utilities.parsing import flatten_dict  # noqa: F401
    from pytorch_lightning.utilities.parsing import save_hyperparameters  # noqa: F401
    from pytorch_lightning.utilities.parsing import AttributeDict  # noqa: F401
    from pytorch_lightning.utilities.parsing import _lightning_get_all_attr_holders  # noqa: F401
    from pytorch_lightning.utilities.parsing import _lightning_get_first_attr_holder  # noqa: F401
    from pytorch_lightning.utilities.parsing import lightning_hasattr  # noqa: F401
    from pytorch_lightning.utilities.parsing import lightning_getattr  # noqa: F401
    from pytorch_lightning.utilities.parsing import lightning_setattr  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
