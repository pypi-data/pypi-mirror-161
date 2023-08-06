try:

    from pytorch_lightning.plugins.environments.bagua_environment import BaguaEnvironment  # noqa: F401
    from pytorch_lightning.plugins.environments.cluster_environment import ClusterEnvironment  # noqa: F401
    from pytorch_lightning.plugins.environments.kubeflow_environment import KubeflowEnvironment  # noqa: F401
    from pytorch_lightning.plugins.environments.lightning_environment import LightningEnvironment  # noqa: F401
    from pytorch_lightning.plugins.environments.lsf_environment import LSFEnvironment  # noqa: F401
    from pytorch_lightning.plugins.environments.slurm_environment import SLURMEnvironment  # noqa: F401
    from pytorch_lightning.plugins.environments.torchelastic_environment import TorchElasticEnvironment  # noqa: F401
    from pytorch_lightning.plugins.environments.xla_environment import XLAEnvironment  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
