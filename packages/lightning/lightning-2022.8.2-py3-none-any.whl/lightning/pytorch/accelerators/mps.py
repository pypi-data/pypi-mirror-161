try:

    from pytorch_lightning.accelerators.mps import _MPS_AVAILABLE  # noqa: F401
    from pytorch_lightning.accelerators.mps import MPSAccelerator  # noqa: F401
    from pytorch_lightning.accelerators.mps import _VM_PERCENT  # noqa: F401
    from pytorch_lightning.accelerators.mps import _PERCENT  # noqa: F401
    from pytorch_lightning.accelerators.mps import _SWAP_PERCENT  # noqa: F401
    from pytorch_lightning.accelerators.mps import get_device_stats  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
