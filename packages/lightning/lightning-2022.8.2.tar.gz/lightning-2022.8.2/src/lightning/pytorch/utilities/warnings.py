try:

    from pytorch_lightning.utilities.warnings import PossibleUserWarning  # noqa: F401
    from pytorch_lightning.utilities.warnings import WarningCache  # noqa: F401
    from pytorch_lightning.utilities.warnings import rank_zero_warn  # noqa: F401
    from pytorch_lightning.utilities.warnings import rank_zero_deprecation  # noqa: F401
    from pytorch_lightning.utilities.warnings import LightningDeprecationWarning  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
