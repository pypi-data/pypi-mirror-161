try:

    from pytorch_lightning.overrides.data_parallel import _ignore_scalar_return_in_dp  # noqa: F401
    from pytorch_lightning.overrides.data_parallel import LightningParallelModule  # noqa: F401
    from pytorch_lightning.overrides.data_parallel import python_scalar_to_tensor  # noqa: F401
    from pytorch_lightning.overrides.data_parallel import unsqueeze_scalar_tensor  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
