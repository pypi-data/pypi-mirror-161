try:
    from typing import Union

    from pytorch_lightning.plugins.environments import ClusterEnvironment
    from pytorch_lightning.plugins.io.async_plugin import AsyncCheckpointIO
    from pytorch_lightning.plugins.io.checkpoint_plugin import CheckpointIO
    from pytorch_lightning.plugins.io.hpu_plugin import HPUCheckpointIO
    from pytorch_lightning.plugins.io.torch_plugin import TorchCheckpointIO
    from pytorch_lightning.plugins.io.xla_plugin import XLACheckpointIO
    from pytorch_lightning.plugins.layer_sync import LayerSync, NativeSyncBatchNorm
    from pytorch_lightning.plugins.precision.apex_amp import ApexMixedPrecisionPlugin
    from pytorch_lightning.plugins.precision.deepspeed import DeepSpeedPrecisionPlugin
    from pytorch_lightning.plugins.precision.double import DoublePrecisionPlugin
    from pytorch_lightning.plugins.precision.fully_sharded_native_amp import FullyShardedNativeMixedPrecisionPlugin
    from pytorch_lightning.plugins.precision.hpu import HPUPrecisionPlugin
    from pytorch_lightning.plugins.precision.ipu import IPUPrecisionPlugin
    from pytorch_lightning.plugins.precision.native_amp import NativeMixedPrecisionPlugin
    from pytorch_lightning.plugins.precision.precision_plugin import PrecisionPlugin
    from pytorch_lightning.plugins.precision.sharded_native_amp import ShardedNativeMixedPrecisionPlugin
    from pytorch_lightning.plugins.precision.tpu import TPUPrecisionPlugin
    from pytorch_lightning.plugins.precision.tpu_bf16 import TPUBf16PrecisionPlugin
    from pytorch_lightning.plugins.training_type.ddp import DDPPlugin
    from pytorch_lightning.plugins.training_type.ddp2 import DDP2Plugin
    from pytorch_lightning.plugins.training_type.ddp_spawn import DDPSpawnPlugin
    from pytorch_lightning.plugins.training_type.deepspeed import DeepSpeedPlugin
    from pytorch_lightning.plugins.training_type.dp import DataParallelPlugin
    from pytorch_lightning.plugins.training_type.fully_sharded import DDPFullyShardedPlugin
    from pytorch_lightning.plugins.training_type.horovod import HorovodPlugin
    from pytorch_lightning.plugins.training_type.ipu import IPUPlugin
    from pytorch_lightning.plugins.training_type.parallel import ParallelPlugin
    from pytorch_lightning.plugins.training_type.sharded import DDPShardedPlugin
    from pytorch_lightning.plugins.training_type.sharded_spawn import DDPSpawnShardedPlugin
    from pytorch_lightning.plugins.training_type.single_device import SingleDevicePlugin
    from pytorch_lightning.plugins.training_type.single_tpu import SingleTPUPlugin
    from pytorch_lightning.plugins.training_type.tpu_spawn import TPUSpawnPlugin
    from pytorch_lightning.plugins.training_type.training_type_plugin import TrainingTypePlugin
    from pytorch_lightning.strategies import Strategy

    from pytorch_lightning.plugins import PLUGIN  # noqa: F401
    from pytorch_lightning.plugins import PLUGIN_INPUT  # noqa: F401
    from pytorch_lightning.plugins import __all__  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
