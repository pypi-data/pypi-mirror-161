from typing import Dict, Union

from pydantic import BaseModel, Field

from servicefoundry.auto_gen.models import (
    DockerFileBuildConfig,
    TfyPythonBuildPackBuildConfig,
)
from servicefoundry.builder.builders import get_builder


class _BuildConfig(BaseModel):
    # I cannot use Field(discriminator="build_config_type") here as
    # build_config_type in the build configs is not a Literal.
    __root__: Union[DockerFileBuildConfig, TfyPythonBuildPackBuildConfig]


def build(build_configuration: Union[BaseModel, Dict], tag: str):
    build_configuration = _BuildConfig.parse_obj(build_configuration).__root__

    # print(type(build_configuration).__module__)
    # This is still `servicefoundry.models`.
    builder = get_builder(build_configuration.type)
    return builder(build_configuration=build_configuration, tag=tag)


if __name__ == "__main__":
    import os
    from tempfile import TemporaryDirectory

    from servicefoundry import models

    with TemporaryDirectory() as local_dir:
        docker_file_path = os.path.join(local_dir, "Dockerfile.test")
        with open(docker_file_path, "w", encoding="utf8") as fp:
            fp.write("from postgres:latest")

        build_config = models.DockerFileBuildConfig(
            build_context_path=local_dir,
            docker_file_path=docker_file_path,
        )

        build(tag="test", build_configuration=build_config)
