try:
    from lightning_app.utilities.cli_helpers import _format_input_env_variables  # noqa: F401

except ImportError as err:

    from os import linesep
    from lightning_app import __version__
    msg = f'Your `lightning` package was built for `lightning_app==0.5.4`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
