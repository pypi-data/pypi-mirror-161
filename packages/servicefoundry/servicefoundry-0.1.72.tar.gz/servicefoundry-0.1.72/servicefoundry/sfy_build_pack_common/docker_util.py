from servicefoundry.sfy_build_pack_common.process_util import execute


def build_docker(name, docker_path=".", docker_file_path=None, cache=None):
    cmd = ["docker", "build", docker_path, "-t", name]
    if docker_file_path:
        cmd.extend(["--file", docker_file_path])
    if cache:
        cmd.extend(["--cache-from", cache])
    for line in execute(cmd):
        print(line)
