try:

    from pytorch_lightning.callbacks.stochastic_weight_avg import _AVG_FN  # noqa: F401
    from pytorch_lightning.callbacks.stochastic_weight_avg import StochasticWeightAveraging  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
