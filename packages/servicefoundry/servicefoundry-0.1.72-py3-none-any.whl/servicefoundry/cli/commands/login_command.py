import logging

import rich_click as click

from servicefoundry.cli.console import console
from servicefoundry.cli.const import COMMAND_CLS
from servicefoundry.cli.io.rich_output_callback import RichOutputCallBack
from servicefoundry.cli.util import handle_exception_wrapper
from servicefoundry.lib.messages import PROMPT_POST_LOGIN
from servicefoundry.lib.session import login

logger = logging.getLogger(__name__)


@click.command(name="login", cls=COMMAND_CLS)
@click.option("--relogin", is_flag=True, default=False)
@handle_exception_wrapper
def login_command(relogin):
    """
    Login to servicefoundry

    \b
    Once logged in, you can initiate a new service with `sfy init`
    and deploy the service with `sfy deploy`
    """
    # TODO (chiragjn): Add support for non interactive login with API key.
    #                  It is supported indirectly as we always look for `SERVICE_FOUNDRY_API_KEY`
    #                  in the environment
    callback = RichOutputCallBack()
    login(interactive=True, output_hook=callback, relogin=relogin)
    console.print(PROMPT_POST_LOGIN)


def get_login_command():
    return login_command
