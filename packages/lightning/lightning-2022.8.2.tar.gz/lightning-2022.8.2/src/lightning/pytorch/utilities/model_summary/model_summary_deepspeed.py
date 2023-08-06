try:

    from pytorch_lightning.utilities.model_summary.model_summary_deepspeed import deepspeed_param_size  # noqa: F401
    from pytorch_lightning.utilities.model_summary.model_summary_deepspeed import DeepSpeedLayerSummary  # noqa: F401
    from pytorch_lightning.utilities.model_summary.model_summary_deepspeed import DeepSpeedSummary  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
