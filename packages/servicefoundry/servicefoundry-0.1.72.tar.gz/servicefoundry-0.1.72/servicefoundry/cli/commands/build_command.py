import json
import logging

import rich_click as click

from servicefoundry import builder
from servicefoundry.cli.const import GROUP_CLS
from servicefoundry.cli.io.rich_output_callback import RichOutputCallBack
from servicefoundry.cli.util import handle_exception_wrapper
from servicefoundry.sfy_build.build import build

logger = logging.getLogger(__name__)


@click.group(
    name="build",
    cls=GROUP_CLS,
    invoke_without_command=True,
    help="Build servicefoundry Service",
)
@click.option("--name", type=click.STRING, default=None)
@click.option("--cache", type=click.STRING, default=None)
@click.option("--build-config", type=click.STRING, default=None)
@handle_exception_wrapper
def build_command(name, cache, build_config):
    if build_config:
        builder.build(build_configuration=json.loads(build_config), tag=name)
        return

    output_hook = RichOutputCallBack()
    build(name, output_hook=output_hook, cache=cache)


def get_build_command():
    return build_command
