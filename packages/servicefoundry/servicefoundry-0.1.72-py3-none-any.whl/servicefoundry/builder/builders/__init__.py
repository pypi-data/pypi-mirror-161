from functools import wraps
from typing import Callable, Dict, TypeVar

from servicefoundry.auto_gen.models import DockerFileBuildConfig
from servicefoundry.builder.builders.docker_file import docker_file_build

BUILD_REGISTRY: Dict[str, Callable] = {
    "dockerfile": docker_file_build,
}


def get_builder(build_configuration_type: str) -> Callable:
    if build_configuration_type not in BUILD_REGISTRY:
        raise NotImplementedError(f"Builder for {build_configuration_type} not found")

    return BUILD_REGISTRY[build_configuration_type]
