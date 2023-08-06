try:

    from pytorch_lightning.accelerators.cpu import CPUAccelerator  # noqa: F401
    from pytorch_lightning.accelerators.cpu import _CPU_VM_PERCENT  # noqa: F401
    from pytorch_lightning.accelerators.cpu import _CPU_PERCENT  # noqa: F401
    from pytorch_lightning.accelerators.cpu import _CPU_SWAP_PERCENT  # noqa: F401
    from pytorch_lightning.accelerators.cpu import get_cpu_stats  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
