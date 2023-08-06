from servicefoundry.sfy_build_pack_common.docker_util import build_docker


def build(name, cache=None, **kwargs):
    build_docker(name, cache=cache)
