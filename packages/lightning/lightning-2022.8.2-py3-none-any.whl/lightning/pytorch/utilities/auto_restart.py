try:

    from pytorch_lightning.utilities.auto_restart import FastForwardSampler  # noqa: F401
    from pytorch_lightning.utilities.auto_restart import IteratorState  # noqa: F401
    from pytorch_lightning.utilities.auto_restart import MergedIteratorState  # noqa: F401
    from pytorch_lightning.utilities.auto_restart import CaptureMapDataset  # noqa: F401
    from pytorch_lightning.utilities.auto_restart import CaptureIterableDataset  # noqa: F401
    from pytorch_lightning.utilities.auto_restart import _find_fast_forward_samplers  # noqa: F401
    from pytorch_lightning.utilities.auto_restart import _cycle_to_next_worker_and_reset  # noqa: F401
    from pytorch_lightning.utilities.auto_restart import _capture_metadata_collate  # noqa: F401
    from pytorch_lightning.utilities.auto_restart import _next_data_wrapper  # noqa: F401
    from pytorch_lightning.utilities.auto_restart import patch_dataloader_iterator  # noqa: F401
    from pytorch_lightning.utilities.auto_restart import _add_capture_metadata_collate  # noqa: F401
    from pytorch_lightning.utilities.auto_restart import _reload_dataloader_state_dict_automatic_map_dataset  # noqa: F401
    from pytorch_lightning.utilities.auto_restart import _reload_dataloader_state_dict_automatic_iterable_dataset  # noqa: F401
    from pytorch_lightning.utilities.auto_restart import _reload_dataloader_state_dict_automatic  # noqa: F401
    from pytorch_lightning.utilities.auto_restart import _reload_dataloader_state_dict_manual  # noqa: F401
    from pytorch_lightning.utilities.auto_restart import _reload_dataloader_state_dict  # noqa: F401
    from pytorch_lightning.utilities.auto_restart import _rotate_worker_indices  # noqa: F401
    from pytorch_lightning.utilities.auto_restart import _StatefulDataLoaderIter  # noqa: F401
    from pytorch_lightning.utilities.auto_restart import _SingleProcessDataLoaderIterStateful  # noqa: F401
    from pytorch_lightning.utilities.auto_restart import _MultiProcessingDataLoaderIterStateful  # noqa: F401
    from pytorch_lightning.utilities.auto_restart import _get_iterator  # noqa: F401
    from pytorch_lightning.utilities.auto_restart import _patch_dataloader_get_iterators  # noqa: F401
    from pytorch_lightning.utilities.auto_restart import _teardown_dataloader_get_iterators  # noqa: F401
    from pytorch_lightning.utilities.auto_restart import _validate_iterable_dataset  # noqa: F401
    from pytorch_lightning.utilities.auto_restart import _validate_map_dataset  # noqa: F401
    from pytorch_lightning.utilities.auto_restart import _validate_fault_tolerant_automatic  # noqa: F401
    from pytorch_lightning.utilities.auto_restart import _collect_states_on_rank_zero_over_collection  # noqa: F401

except ImportError as err:

    from os import linesep
    from pytorch_lightning import __version__
    msg = f'Your `lightning` package was built for `pytorch_lightning==1.7.0`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
