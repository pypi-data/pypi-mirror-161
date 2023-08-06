from servicefoundry.auto_gen.models import DockerFileBuildConfig
from servicefoundry.builder.utils import build_docker_image


def docker_file_build(tag: str, build_configuration: DockerFileBuildConfig):
    build_docker_image(
        tag=tag,
        path=build_configuration.build_context_path,
        file=build_configuration.docker_file_path,
    )
