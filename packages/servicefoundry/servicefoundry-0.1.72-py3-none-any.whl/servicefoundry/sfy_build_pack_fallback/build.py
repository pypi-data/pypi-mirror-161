from servicefoundry.sfy_build_pack_common.process_util import execute

BUILDER = "builder"
DEFAULT_BUILDER = "paketobuildpacks/builder:base"


def build(name, options=None, **kwargs):
    builder = DEFAULT_BUILDER
    if options and BUILDER in options:
        builder = options[BUILDER]
    for line in execute(["pack", "build", name, f"--{BUILDER}", builder]):
        print(line)
