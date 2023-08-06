try:
    from lightning_app.utilities.name_generator import _adjectives  # noqa: F401
    from lightning_app.utilities.name_generator import _surnames  # noqa: F401
    from lightning_app.utilities.name_generator import get_unique_name  # noqa: F401

except ImportError as err:

    from os import linesep
    from lightning_app import __version__
    msg = f'Your `lightning` package was built for `lightning_app==0.5.4`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
