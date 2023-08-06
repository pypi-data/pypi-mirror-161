try:

    from pytorch_lightning.utilities.cli import _deprecate_registry_message  # noqa: F401
    from pytorch_lightning.utilities.cli import _deprecate_auto_registry_message  # noqa: F401
    from pytorch_lightning.utilities.cli import _Registry  # noqa: F401
    from pytorch_lightning.utilities.cli import OPTIMIZER_REGISTRY  # noqa: F401
    from pytorch_lightning.utilities.cli import LR_SCHEDULER_REGISTRY  # noqa: F401
    from pytorch_lightning.utilities.cli import CALLBACK_REGISTRY  # noqa: F401
    from pytorch_lightning.utilities.cli import MODEL_REGISTRY  # noqa: F401
    from pytorch_lightning.utilities.cli import DATAMODULE_REGISTRY  # noqa: F401
    from pytorch_lightning.utilities.cli import LOGGER_REGISTRY  # noqa: F401
    from pytorch_lightning.utilities.cli import _populate_registries  # noqa: F401
    from pytorch_lightning.utilities.cli import _deprecation  # noqa: F401
    from pytorch_lightning.utilities.cli import LightningArgumentParser  # noqa: F401
    from pytorch_lightning.utilities.cli import SaveConfigCallback  # noqa: F401
    from pytorch_lightning.utilities.cli import LightningCLI  # noqa: F401
    from pytorch_lightning.utilities.cli import instantiate_class  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
