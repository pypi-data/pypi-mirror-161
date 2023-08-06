try:

    from pytorch_lightning.utilities.apply_func import _CPU_DEVICES  # noqa: F401
    from pytorch_lightning.utilities.apply_func import to_dtype_tensor  # noqa: F401
    from pytorch_lightning.utilities.apply_func import from_numpy  # noqa: F401
    from pytorch_lightning.utilities.apply_func import CONVERSION_DTYPES  # noqa: F401
    from pytorch_lightning.utilities.apply_func import _is_namedtuple  # noqa: F401
    from pytorch_lightning.utilities.apply_func import _is_dataclass_instance  # noqa: F401
    from pytorch_lightning.utilities.apply_func import apply_to_collection  # noqa: F401
    from pytorch_lightning.utilities.apply_func import apply_to_collections  # noqa: F401
    from pytorch_lightning.utilities.apply_func import TransferableDataType  # noqa: F401
    from pytorch_lightning.utilities.apply_func import move_data_to_device  # noqa: F401
    from pytorch_lightning.utilities.apply_func import convert_to_tensors  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
