from os.path import join

from servicefoundry.sfy_build_pack_common.docker_util import build_docker
from servicefoundry.sfy_build_pack_common.file_util import write_file
from servicefoundry.sfy_build_pack_python.docker_file import (
    PYTHON_39,
    BaseDockerFile,
    Honcho,
    Requirements,
)

PYTHON_VERSION = "python_version"


def generate_docker_file(python_version):
    return BaseDockerFile(
        layers=[Requirements(), Honcho()], base_image=python_version
    ).to_dockerfile()


def build(name, build_dir, options=None, cache=None, **kwargs):
    if options and PYTHON_VERSION in options:
        python_version = options[PYTHON_VERSION]
    else:
        python_version = PYTHON_39
    docker_file_str = generate_docker_file(python_version)
    docker_file = join(build_dir, "Dockerfile")
    write_file(docker_file, docker_file_str)
    build_docker(name, docker_file_path=docker_file, cache=cache)
