from pathlib import Path

from personal_data_governance.config.loaders import (
    DEFAULT_SERVICE_REGISTRY_FILE,
    LoadedServiceRegistry,
    load_service_registry,
)


def build_initial_service_registry(
    configuration_file: Path = (
        DEFAULT_SERVICE_REGISTRY_FILE
    ),
) -> LoadedServiceRegistry:
    return load_service_registry(
        configuration_file
    )
