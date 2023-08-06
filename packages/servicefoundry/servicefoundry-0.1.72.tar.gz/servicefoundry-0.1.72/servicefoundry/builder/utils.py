from typing import Optional

from servicefoundry.sfy_build_pack_common.process_util import execute


def build_docker_image(tag: str, path: str = ".", file: Optional[str] = None):
    cmd = ["docker", "build", path, "-t", tag]
    if file:
        cmd.extend(["--file", file])
    for line in execute(cmd):
        print(line)
