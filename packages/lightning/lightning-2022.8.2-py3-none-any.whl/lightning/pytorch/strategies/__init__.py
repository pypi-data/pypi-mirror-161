try:

    from pytorch_lightning.strategies.bagua import BaguaStrategy  # noqa: F401
    from pytorch_lightning.strategies.ddp import DDPStrategy  # noqa: F401
    from pytorch_lightning.strategies.ddp2 import DDP2Strategy  # noqa: F401
    from pytorch_lightning.strategies.ddp_spawn import DDPSpawnStrategy  # noqa: F401
    from pytorch_lightning.strategies.deepspeed import DeepSpeedStrategy  # noqa: F401
    from pytorch_lightning.strategies.dp import DataParallelStrategy  # noqa: F401
    from pytorch_lightning.strategies.fully_sharded import DDPFullyShardedStrategy  # noqa: F401
    from pytorch_lightning.strategies.fully_sharded_native import DDPFullyShardedNativeStrategy  # noqa: F401
    from pytorch_lightning.strategies.hivemind import HivemindStrategy  # noqa: F401
    from pytorch_lightning.strategies.horovod import HorovodStrategy  # noqa: F401
    from pytorch_lightning.strategies.hpu_parallel import HPUParallelStrategy  # noqa: F401
    from pytorch_lightning.strategies.ipu import IPUStrategy  # noqa: F401
    from pytorch_lightning.strategies.parallel import ParallelStrategy  # noqa: F401
    from pytorch_lightning.strategies.sharded import DDPShardedStrategy  # noqa: F401
    from pytorch_lightning.strategies.sharded_spawn import DDPSpawnShardedStrategy  # noqa: F401
    from pytorch_lightning.strategies.single_device import SingleDeviceStrategy  # noqa: F401
    from pytorch_lightning.strategies.single_hpu import SingleHPUStrategy  # noqa: F401
    from pytorch_lightning.strategies.single_tpu import SingleTPUStrategy  # noqa: F401
    from pytorch_lightning.strategies.strategy import Strategy  # noqa: F401
    from pytorch_lightning.strategies.strategy_registry import call_register_strategies, StrategyRegistry  # noqa: F401
    from pytorch_lightning.strategies.tpu_spawn import TPUSpawnStrategy  # noqa: F401

    from pytorch_lightning.strategies import STRATEGIES_BASE_MODULE  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
