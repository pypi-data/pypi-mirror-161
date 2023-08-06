try:

    from pytorch_lightning.tuner.auto_gpu_select import pick_multiple_gpus  # noqa: F401
    from pytorch_lightning.tuner.auto_gpu_select import pick_single_gpu  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
