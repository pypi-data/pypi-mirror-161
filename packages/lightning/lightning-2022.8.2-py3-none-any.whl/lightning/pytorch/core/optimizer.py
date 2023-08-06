try:

    from pytorch_lightning.core.optimizer import do_nothing_closure  # noqa: F401
    from pytorch_lightning.core.optimizer import LightningOptimizer  # noqa: F401
    from pytorch_lightning.core.optimizer import _init_optimizers_and_lr_schedulers  # noqa: F401
    from pytorch_lightning.core.optimizer import _configure_optimizers  # noqa: F401
    from pytorch_lightning.core.optimizer import _configure_schedulers_automatic_opt  # noqa: F401
    from pytorch_lightning.core.optimizer import _configure_schedulers_manual_opt  # noqa: F401
    from pytorch_lightning.core.optimizer import _validate_scheduler_api  # noqa: F401
    from pytorch_lightning.core.optimizer import _set_scheduler_opt_idx  # noqa: F401
    from pytorch_lightning.core.optimizer import _validate_optim_conf  # noqa: F401
    from pytorch_lightning.core.optimizer import _MockOptimizer  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
