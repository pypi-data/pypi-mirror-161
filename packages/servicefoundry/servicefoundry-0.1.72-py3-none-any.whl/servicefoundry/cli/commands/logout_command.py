import logging

import rich_click as click

from servicefoundry.cli.const import COMMAND_CLS
from servicefoundry.cli.io.rich_output_callback import RichOutputCallBack
from servicefoundry.cli.util import handle_exception_wrapper
from servicefoundry.lib.session import logout

logger = logging.getLogger(__name__)


@click.command(name="logout", cls=COMMAND_CLS)
@handle_exception_wrapper
def logout_command():
    """
    Logout current servicefoundry session
    """
    callback = RichOutputCallBack()
    logout(output_hook=callback)


def get_logout_command():
    return logout_command
