from typing import Optional

import rich_click as click

from servicefoundry.cli.console import console
from servicefoundry.io.output_callback import OutputCallBack
from servicefoundry.lib.clients.auth_service_client import AuthServiceClient
from servicefoundry.lib.clients.service_foundry_client import (
    ServiceFoundryServiceClient,
)
from servicefoundry.lib.config_utils import _get_profile
from servicefoundry.lib.const import DEFAULT_PROFILE_NAME, SFY_SESSIONS_FILEPATH
from servicefoundry.lib.exceptions import BadRequestException
from servicefoundry.lib.messages import (
    PROMPT_ALREADY_LOGGED_OUT,
    PROMPT_LOGIN_INFO,
    PROMPT_LOGIN_SUCCESSFUL,
    PROMPT_LOGOUT_SUCCESSFUL,
    PROMPT_SETTING_CLUSTER_CONTEXT,
)
from servicefoundry.lib.model.entity import Cluster, Profile
from servicefoundry.lib.model.session import ServiceFoundrySession
from servicefoundry.lib.session_factory import get_session, logout_session


def _set_tenant_default_cluster_if_any():
    client = ServiceFoundryServiceClient.get_client()
    clusters = client.list_cluster()
    for cluster in clusters:
        cluster = Cluster.from_dict(cluster)
        if cluster.isTenantDefault:
            console.print(PROMPT_SETTING_CLUSTER_CONTEXT.format(cluster.name))
            client.session.set_cluster(cluster.to_dict_for_session())
            client.session.save_session()
            return


def _login_using_device_code(
    profile: Profile, output_hook: OutputCallBack
) -> ServiceFoundrySession:
    auth_client = AuthServiceClient(profile=profile)
    url, user_code, device_code = auth_client.get_device_code()
    output_hook.print_line(f"Login Code: {user_code}")
    output_hook.print_line(
        f"Waiting for authentication. Go to the following url to complete the authentication: {url}"
    )
    click.launch(url)
    session = auth_client.poll_for_auth(device_code)
    session.save_session()
    output_hook.print_line(PROMPT_LOGIN_SUCCESSFUL)
    output_hook.print_line(f"Session stored at {SFY_SESSIONS_FILEPATH}")
    return session


def _login_with_api_key(
    profile: Profile, api_key: str, output_hook: OutputCallBack
) -> ServiceFoundrySession:
    session = AuthServiceClient(profile=profile).login_with_api_token(api_key=api_key)
    session.save_session()
    output_hook.print_line(PROMPT_LOGIN_SUCCESSFUL)
    return session


def _login(
    profile: Profile,
    api_key: Optional[str] = None,
    interactive: bool = False,
    output_hook=OutputCallBack(),
):
    if interactive:
        session = _login_using_device_code(profile=profile, output_hook=output_hook)
    else:
        if not api_key:
            raise ValueError("`api_key` is required in non interactive mode")
        session = _login_with_api_key(
            profile=profile, api_key=api_key, output_hook=output_hook
        )
    _set_tenant_default_cluster_if_any()
    return session


def login(
    api_key: Optional[str] = None,
    interactive: bool = False,
    output_hook=OutputCallBack(),
    relogin: bool = False,
):
    # TODO (chiragjn): Expose profiles in future
    profile_name = DEFAULT_PROFILE_NAME
    profile = _get_profile(name=profile_name)
    if relogin:
        session = _login(
            profile=profile,
            api_key=api_key,
            interactive=interactive,
            output_hook=output_hook,
        )
    else:
        try:
            session = get_session(profile_name=profile_name)
        except BadRequestException:
            session = _login(
                profile=profile,
                api_key=api_key,
                interactive=interactive,
                output_hook=output_hook,
            )
    user = session.get_user_details()
    output_hook.print_line(
        PROMPT_LOGIN_INFO.format(username=user["username"], email=user["email"])
    )


def logout(output_hook=OutputCallBack()):
    # TODO (chiragjn): Expose profiles in future
    profile_name = DEFAULT_PROFILE_NAME
    try:
        logout_session(profile_name=profile_name)
    except BadRequestException:
        output_hook.print_line(PROMPT_ALREADY_LOGGED_OUT)
    else:
        output_hook.print_line(PROMPT_LOGOUT_SUCCESSFUL)
