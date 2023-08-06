try:

    import logging
    from typing import Any

    from pytorch_lightning import __about__
    from pytorch_lightning.__about__ import *  # noqa: F401, F403

    if not hasattr(__about__, "__version__"):
        from pytorch_lightning.__version__ import version as __version__  # noqa: F401

    from pytorch_lightning import _DETAIL  # noqa: F401
    from pytorch_lightning import _detail  # noqa: F401
    from pytorch_lightning import logging  # noqa: F401
    from pytorch_lightning import _root_logger  # noqa: F401
    from pytorch_lightning import _logger  # noqa: F401

    from pytorch_lightning.callbacks import Callback  # noqa: E402
    from pytorch_lightning.core import LightningDataModule, LightningModule  # noqa: E402
    from pytorch_lightning.trainer import Trainer  # noqa: E402
    from pytorch_lightning.utilities.seed import seed_everything  # noqa: E402

    from pytorch_lightning import __all__  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
