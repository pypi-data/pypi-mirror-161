try:

    from pytorch_lightning.callbacks.quantization import wrap_qat_forward_context  # noqa: F401
    from pytorch_lightning.callbacks.quantization import wrap_quantize_forward_context  # noqa: F401
    from pytorch_lightning.callbacks.quantization import _recursive_hasattr  # noqa: F401
    from pytorch_lightning.callbacks.quantization import QuantizationAwareTraining  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
