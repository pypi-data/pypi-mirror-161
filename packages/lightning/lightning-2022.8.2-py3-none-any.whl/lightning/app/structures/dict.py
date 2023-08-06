try:

    from lightning_app.structures.dict import T  # noqa: F401
    from lightning_app.structures.dict import _prepare_name  # noqa: F401
    from lightning_app.structures.dict import Dict  # noqa: F401

except ImportError as err:

    from os import linesep
    from lightning_app import __version__
    msg = f'Your `lightning` package was built for `lightning_app==0.5.4`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
