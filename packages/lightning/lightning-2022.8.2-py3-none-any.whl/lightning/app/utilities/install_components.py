try:
    from lightning_app.utilities.install_components import _PACKAGE_REGISTRY_COMMANDS  # noqa: F401
    from lightning_app.utilities.install_components import logger  # noqa: F401
    from lightning_app.utilities.install_components import _PYTHON_GREATER_EQUAL_3_8_0  # noqa: F401
    from lightning_app.utilities.install_components import _LIGHTNING_ENTRYPOINT  # noqa: F401
    from lightning_app.utilities.install_components import _ensure_package_exists  # noqa: F401
    from lightning_app.utilities.install_components import _import_external_component_classes  # noqa: F401
    from lightning_app.utilities.install_components import register_all_external_components  # noqa: F401
    from lightning_app.utilities.install_components import _pip_uninstall_component_package  # noqa: F401
    from lightning_app.utilities.install_components import _pip_install_component_package  # noqa: F401
    from lightning_app.utilities.install_components import _extract_public_package_name_from_entrypoint  # noqa: F401
    from lightning_app.utilities.install_components import install_external_component  # noqa: F401

except ImportError as err:

    from os import linesep
    from lightning_app import __version__
    msg = f'Your `lightning` package was built for `lightning_app==0.5.4`, but you are running {__version__}'
    raise type(err)(str(err) + linesep + msg)
