try:

    from pytorch_lightning.callbacks.device_stats_monitor import DeviceStatsMonitor  # noqa: F401
    from pytorch_lightning.callbacks.device_stats_monitor import _prefix_metric_keys  # noqa: F401
    from pytorch_lightning.callbacks.device_stats_monitor import prefix_metric_keys  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
