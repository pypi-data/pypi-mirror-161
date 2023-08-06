try:

    from pytorch_lightning.utilities.deepspeed import CPU_DEVICE  # noqa: F401
    from pytorch_lightning.utilities.deepspeed import ds_checkpoint_dir  # noqa: F401
    from pytorch_lightning.utilities.deepspeed import convert_zero_checkpoint_to_fp32_state_dict  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
