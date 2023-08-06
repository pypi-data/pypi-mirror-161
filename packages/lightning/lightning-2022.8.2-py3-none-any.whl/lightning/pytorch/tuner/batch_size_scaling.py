try:

    from pytorch_lightning.tuner.batch_size_scaling import log  # noqa: F401
    from pytorch_lightning.tuner.batch_size_scaling import scale_batch_size  # noqa: F401
    from pytorch_lightning.tuner.batch_size_scaling import _run_power_scaling  # noqa: F401
    from pytorch_lightning.tuner.batch_size_scaling import _run_binsearch_scaling  # noqa: F401
    from pytorch_lightning.tuner.batch_size_scaling import _adjust_batch_size  # noqa: F401
    from pytorch_lightning.tuner.batch_size_scaling import _is_valid_batch_size  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
