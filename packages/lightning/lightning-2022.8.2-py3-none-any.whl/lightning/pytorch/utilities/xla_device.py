try:

    from pytorch_lightning.utilities.xla_device import TPU_CHECK_TIMEOUT  # noqa: F401
    from pytorch_lightning.utilities.xla_device import inner_f  # noqa: F401
    from pytorch_lightning.utilities.xla_device import pl_multi_process  # noqa: F401
    from pytorch_lightning.utilities.xla_device import XLADeviceUtils  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
