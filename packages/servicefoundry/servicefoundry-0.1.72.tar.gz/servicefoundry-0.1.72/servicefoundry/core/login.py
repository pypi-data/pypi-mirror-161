from servicefoundry.core.notebook.notebook_util import get_default_callback
from servicefoundry.lib import session


def login(api_key=None):
    session.login(
        api_key=api_key,
        interactive=False if api_key else True,
        output_hook=get_default_callback(),
    )
