try:

    from pytorch_lightning.accelerators.accelerator import Accelerator  # noqa: F401
    from pytorch_lightning.accelerators.cpu import CPUAccelerator  # noqa: F401
    from pytorch_lightning.accelerators.cuda import CUDAAccelerator  # noqa: F401
    from pytorch_lightning.accelerators.gpu import GPUAccelerator  # noqa: F401
    from pytorch_lightning.accelerators.hpu import HPUAccelerator  # noqa: F401
    from pytorch_lightning.accelerators.ipu import IPUAccelerator  # noqa: F401
    from pytorch_lightning.accelerators.mps import MPSAccelerator  # noqa: F401
    from pytorch_lightning.accelerators.registry import AcceleratorRegistry, call_register_accelerators  # noqa: F401
    from pytorch_lightning.accelerators.tpu import TPUAccelerator  # noqa: F401

    from pytorch_lightning.accelerators import ACCELERATORS_BASE_MODULE  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
