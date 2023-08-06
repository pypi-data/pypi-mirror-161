import logging

import rich_click as click

from servicefoundry.cli.const import COMMAND_CLS
from servicefoundry.cli.io.cli_input_hook import CliInputHook
from servicefoundry.cli.io.rich_output_callback import RichOutputCallBack
from servicefoundry.cli.util import handle_exception_wrapper
from servicefoundry.sfy_init.init import init, init_from_template

logger = logging.getLogger(__name__)


@click.command(
    name="init", cls=COMMAND_CLS, help="Initialize a new Service for servicefoundry"
)
@click.option("--from-template", is_flag=True, default=False)
@handle_exception_wrapper
def init_command(from_template):
    input_hook = CliInputHook()
    output_hook = RichOutputCallBack()
    if from_template:
        init_from_template(input_hook, output_hook)
    else:
        init(input_hook, output_hook)


def get_init_command():
    return init_command
