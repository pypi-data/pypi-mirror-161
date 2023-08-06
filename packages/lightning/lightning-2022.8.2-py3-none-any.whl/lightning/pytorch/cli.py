try:

    from pytorch_lightning.cli import _JSONARGPARSE_SIGNATURES_AVAILABLE  # noqa: F401
    from pytorch_lightning.cli import ReduceLROnPlateau  # noqa: F401
    from pytorch_lightning.cli import LRSchedulerTypeTuple  # noqa: F401
    from pytorch_lightning.cli import LRSchedulerTypeUnion  # noqa: F401
    from pytorch_lightning.cli import LRSchedulerType  # noqa: F401
    from pytorch_lightning.cli import LightningArgumentParser  # noqa: F401
    from pytorch_lightning.cli import SaveConfigCallback  # noqa: F401
    from pytorch_lightning.cli import LightningCLI  # noqa: F401
    from pytorch_lightning.cli import _class_path_from_class  # noqa: F401
    from pytorch_lightning.cli import _global_add_class_path  # noqa: F401
    from pytorch_lightning.cli import _add_class_path_generator  # noqa: F401
    from pytorch_lightning.cli import instantiate_class  # noqa: F401
    from pytorch_lightning.cli import _get_short_description  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
