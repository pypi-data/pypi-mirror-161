try:

    from pytorch_lightning.trainer.configuration_validator import verify_loop_configurations  # noqa: F401
    from pytorch_lightning.trainer.configuration_validator import _check_on_hpc_hooks  # noqa: F401
    from pytorch_lightning.trainer.configuration_validator import _check_on_epoch_start_end  # noqa: F401
    from pytorch_lightning.trainer.configuration_validator import _check_on_pretrain_routine  # noqa: F401
    from pytorch_lightning.trainer.configuration_validator import _check_deprecated_callback_hooks  # noqa: F401
    from pytorch_lightning.trainer.configuration_validator import _check_precision_plugin_checkpoint_hooks  # noqa: F401
    from pytorch_lightning.trainer.configuration_validator import _check_datamodule_checkpoint_hooks  # noqa: F401
    from pytorch_lightning.trainer.configuration_validator import _check_setup_method  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
