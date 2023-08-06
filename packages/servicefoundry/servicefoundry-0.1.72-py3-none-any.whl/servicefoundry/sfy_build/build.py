import os
import sys

from servicefoundry.io.output_callback import OutputCallBack
from servicefoundry.service_definition.definition import ServiceFoundryDefinition
from servicefoundry.sfy_build.build_pack import detect_build_pack, get_build_pack
from servicefoundry.sfy_build.const import BUILD_DIR, SERVICEFOUNDRY_YAML
from servicefoundry.sfy_build_pack_common.file_util import create_dir


def build(name, output_hook: OutputCallBack, cache: str = None):
    sfy_yaml: ServiceFoundryDefinition = None
    if os.path.isfile(SERVICEFOUNDRY_YAML):
        sfy_yaml = ServiceFoundryDefinition.from_yaml(SERVICEFOUNDRY_YAML)

    if name:
        image_name = name
    elif sfy_yaml and sfy_yaml.service and sfy_yaml.service.name:
        image_name = sfy_yaml.service.name
    else:
        image_name = os.path.basename(os.getcwd())

    options = None
    if sfy_yaml and sfy_yaml.build and sfy_yaml.build.build_pack:
        build_pack = get_build_pack(sfy_yaml.build.build_pack)
        if sfy_yaml.build.options:
            options = sfy_yaml.build.options
    else:
        build_pack = detect_build_pack()

    if build_pack is None:
        output_hook.print_line("No build pack configured to build this package.")
        sys.exit(1)

    output_hook.print_line(f"Going to use build pack {build_pack.name}")
    create_dir(BUILD_DIR)
    build_pack.build(
        name=image_name,
        build_dir=BUILD_DIR,
        options=options,
        output_hook=output_hook,
        cache=cache,
    )
    output_hook.print_line("")
    output_hook.print_line(
        f"Created docker image {image_name}. "
        f"You can use command `docker run -it fastapi-service` to run this service."
    )
