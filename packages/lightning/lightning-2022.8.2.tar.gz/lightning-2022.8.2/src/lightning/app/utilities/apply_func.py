try:

    from lightning_app.utilities.apply_func import _is_namedtuple  # noqa: F401
    from lightning_app.utilities.apply_func import _is_dataclass_instance  # noqa: F401
    from lightning_app.utilities.apply_func import apply_to_collection  # noqa: F401

except ImportError as err:

    from os import linesep
    from lightning_app import __version__
    msg = f'Your `lightning` package was built for `lightning_app==0.5.4`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
