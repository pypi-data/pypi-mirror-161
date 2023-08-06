try:

    from pytorch_lightning.loops.dataloader.evaluation_loop import EvaluationLoop  # noqa: F401
    from pytorch_lightning.loops.dataloader.evaluation_loop import _select_data_fetcher_type  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
