try:

    from pytorch_lightning.utilities.meta import _TORCH_GREATER_EQUAL_1_10  # noqa: F401
    if _TORCH_GREATER_EQUAL_1_10:
        from pytorch_lightning.utilities.meta import enable_python_mode  # noqa: F401
        from pytorch_lightning.utilities.meta import _tls  # noqa: F401
        from pytorch_lightning.utilities.meta import _no_dispatch  # noqa: F401
        from pytorch_lightning.utilities.meta import _handle_arange  # noqa: F401
        from pytorch_lightning.utilities.meta import _handle_tril  # noqa: F401
        from pytorch_lightning.utilities.meta import _MetaContext  # noqa: F401
        from pytorch_lightning.utilities.meta import init_meta  # noqa: F401
        from pytorch_lightning.utilities.meta import is_meta_init  # noqa: F401
    from pytorch_lightning.utilities.meta import get_all_subclasses  # noqa: F401
    from pytorch_lightning.utilities.meta import recursively_setattr  # noqa: F401
    from pytorch_lightning.utilities.meta import materialize_module  # noqa: F401
    from pytorch_lightning.utilities.meta import _unset_meta_device  # noqa: F401
    from pytorch_lightning.utilities.meta import _set_meta_device_populated  # noqa: F401
    from pytorch_lightning.utilities.meta import _set_meta_device  # noqa: F401
    from pytorch_lightning.utilities.meta import init_meta_context  # noqa: F401
    from pytorch_lightning.utilities.meta import is_on_meta_device  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
