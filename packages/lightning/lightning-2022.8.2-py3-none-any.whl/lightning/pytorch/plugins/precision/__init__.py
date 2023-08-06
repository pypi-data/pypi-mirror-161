try:

    from pytorch_lightning.plugins.precision.apex_amp import ApexMixedPrecisionPlugin  # noqa: F401
    from pytorch_lightning.plugins.precision.deepspeed import DeepSpeedPrecisionPlugin  # noqa: F401
    from pytorch_lightning.plugins.precision.double import DoublePrecisionPlugin  # noqa: F401
    from pytorch_lightning.plugins.precision.fully_sharded_native_amp import (  # noqa: F401
        FullyShardedNativeMixedPrecisionPlugin,
    )
    from pytorch_lightning.plugins.precision.hpu import HPUPrecisionPlugin  # noqa: F401
    from pytorch_lightning.plugins.precision.ipu import IPUPrecisionPlugin  # noqa: F401
    from pytorch_lightning.plugins.precision.mixed import MixedPrecisionPlugin  # noqa: F401
    from pytorch_lightning.plugins.precision.native_amp import NativeMixedPrecisionPlugin  # noqa: F401
    from pytorch_lightning.plugins.precision.precision_plugin import PrecisionPlugin  # noqa: F401
    from pytorch_lightning.plugins.precision.sharded_native_amp import ShardedNativeMixedPrecisionPlugin  # noqa: F401
    from pytorch_lightning.plugins.precision.tpu import TPUPrecisionPlugin  # noqa: F401
    from pytorch_lightning.plugins.precision.tpu_bf16 import TPUBf16PrecisionPlugin  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
