try:

    from pytorch_lightning.plugins.environments.lightning_environment import LightningEnvironment  # noqa: F401
    from pytorch_lightning.plugins.environments.lightning_environment import find_free_network_port  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
