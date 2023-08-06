try:

    from pytorch_lightning.loops.epoch.training_epoch_loop import _OUTPUTS_TYPE  # noqa: F401
    from pytorch_lightning.loops.epoch.training_epoch_loop import TrainingEpochLoop  # noqa: F401
    from pytorch_lightning.loops.epoch.training_epoch_loop import _convert_optim_dict  # noqa: F401
    from pytorch_lightning.loops.epoch.training_epoch_loop import _recursive_unpad  # noqa: F401
    from pytorch_lightning.loops.epoch.training_epoch_loop import _recursive_pad  # noqa: F401
    from pytorch_lightning.loops.epoch.training_epoch_loop import _get_dimensions  # noqa: F401
    from pytorch_lightning.loops.epoch.training_epoch_loop import _get_max_shape  # noqa: F401
    from pytorch_lightning.loops.epoch.training_epoch_loop import _iterate_nested_array  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
