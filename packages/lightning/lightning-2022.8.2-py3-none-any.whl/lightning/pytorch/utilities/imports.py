try:

    from pytorch_lightning.utilities.imports import _package_available  # noqa: F401
    from pytorch_lightning.utilities.imports import _module_available  # noqa: F401
    from pytorch_lightning.utilities.imports import _compare_version  # noqa: F401
    from pytorch_lightning.utilities.imports import _RequirementAvailable  # noqa: F401
    from pytorch_lightning.utilities.imports import _IS_WINDOWS  # noqa: F401
    from pytorch_lightning.utilities.imports import _IS_INTERACTIVE  # noqa: F401
    from pytorch_lightning.utilities.imports import _PYTHON_GREATER_EQUAL_3_8_0  # noqa: F401
    from pytorch_lightning.utilities.imports import _TORCH_GREATER_EQUAL_1_9_1  # noqa: F401
    from pytorch_lightning.utilities.imports import _TORCH_GREATER_EQUAL_1_10  # noqa: F401
    from pytorch_lightning.utilities.imports import _TORCH_LESSER_EQUAL_1_10_2  # noqa: F401
    from pytorch_lightning.utilities.imports import _TORCH_GREATER_EQUAL_1_11  # noqa: F401
    from pytorch_lightning.utilities.imports import _TORCH_GREATER_EQUAL_1_12  # noqa: F401
    from pytorch_lightning.utilities.imports import _TORCH_GREATER_EQUAL_1_13  # noqa: F401
    from pytorch_lightning.utilities.imports import _APEX_AVAILABLE  # noqa: F401
    from pytorch_lightning.utilities.imports import _DALI_AVAILABLE  # noqa: F401
    from pytorch_lightning.utilities.imports import _FAIRSCALE_AVAILABLE  # noqa: F401
    from pytorch_lightning.utilities.imports import _FAIRSCALE_OSS_FP16_BROADCAST_AVAILABLE  # noqa: F401
    from pytorch_lightning.utilities.imports import _FAIRSCALE_FULLY_SHARDED_AVAILABLE  # noqa: F401
    from pytorch_lightning.utilities.imports import _GROUP_AVAILABLE  # noqa: F401
    from pytorch_lightning.utilities.imports import _HABANA_FRAMEWORK_AVAILABLE  # noqa: F401
    from pytorch_lightning.utilities.imports import _HIVEMIND_AVAILABLE  # noqa: F401
    from pytorch_lightning.utilities.imports import _HOROVOD_AVAILABLE  # noqa: F401
    from pytorch_lightning.utilities.imports import _HYDRA_AVAILABLE  # noqa: F401
    from pytorch_lightning.utilities.imports import _HYDRA_EXPERIMENTAL_AVAILABLE  # noqa: F401
    from pytorch_lightning.utilities.imports import _KINETO_AVAILABLE  # noqa: F401
    from pytorch_lightning.utilities.imports import _OMEGACONF_AVAILABLE  # noqa: F401
    from pytorch_lightning.utilities.imports import _POPTORCH_AVAILABLE  # noqa: F401
    from pytorch_lightning.utilities.imports import _PSUTIL_AVAILABLE  # noqa: F401
    from pytorch_lightning.utilities.imports import _RICH_AVAILABLE  # noqa: F401
    from pytorch_lightning.utilities.imports import _TORCH_QUANTIZE_AVAILABLE  # noqa: F401
    from pytorch_lightning.utilities.imports import _TORCHTEXT_AVAILABLE  # noqa: F401
    from pytorch_lightning.utilities.imports import _TORCHTEXT_LEGACY  # noqa: F401
    from pytorch_lightning.utilities.imports import _TORCHVISION_AVAILABLE  # noqa: F401
    from pytorch_lightning.utilities.imports import _XLA_AVAILABLE  # noqa: F401
    from pytorch_lightning.utilities.imports import _TPU_AVAILABLE  # noqa: F401
    if _POPTORCH_AVAILABLE:

        from pytorch_lightning.utilities.imports import _IPU_AVAILABLE  # noqa: F401
    if _HABANA_FRAMEWORK_AVAILABLE:
        from pytorch_lightning.utilities.imports import _HPU_AVAILABLE  # noqa: F401
    from pytorch_lightning.utilities.imports import _fault_tolerant_training  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
