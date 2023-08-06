from servicefoundry.core.notebook.notebook_util import get_default_callback
from servicefoundry.lib import session


def logout():
    session.logout(output_hook=get_default_callback())
