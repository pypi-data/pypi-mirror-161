# TODO: rename this file to config.py

from typing import Any, Optional

from servicefoundry.cli.console import console
from servicefoundry.lib.clients.service_foundry_client import (
    ServiceFoundryServiceClient,
)
from servicefoundry.lib.config_utils import _get_profile, _save_profile, _save_session
from servicefoundry.lib.const import DEFAULT_PROFILE_NAME
from servicefoundry.lib.messages import (
    PROMPT_LOGIN_POST_TENANT_CHANGE,
    PROMPT_SETTING_CLUSTER_CONTEXT,
    PROMPT_SETTING_WORKSPACE_CONTEXT,
)
from servicefoundry.lib.model.entity import Cluster, ServerConfig, Workspace
from servicefoundry.lib.util import resolve_cluster_or_error, resolve_workspace_or_error


def use_server(url: str) -> Any:
    # TODO (chiragjn): Expose profiles in future
    profile_name = DEFAULT_PROFILE_NAME
    profile = _get_profile(name=profile_name)
    existing_tenant_name = profile.server_config.tenant_name
    new_server_config = ServerConfig.from_base_url(base_url=url)
    profile.server_config = new_server_config
    _save_profile(profile=profile)
    if existing_tenant_name != new_server_config.tenant_name:
        _save_session(session={}, profile_name=profile_name)
        console.print(PROMPT_LOGIN_POST_TENANT_CHANGE)


def use_cluster(
    name_or_id: Optional[str] = None,
    non_interactive: bool = True,
    client: Optional[ServiceFoundryServiceClient] = None,
) -> Cluster:
    client = client or ServiceFoundryServiceClient.get_client()
    cluster = resolve_cluster_or_error(
        name_or_id=name_or_id,
        non_interactive=non_interactive,
        ignore_context=True,
        client=client,
    )
    client.session.set_cluster(cluster.to_dict_for_session())
    console.print(PROMPT_SETTING_CLUSTER_CONTEXT.format(cluster.name))
    client.session.save_session()
    return cluster


def use_workspace(
    name_or_id: Optional[str] = None,
    cluster_name_or_id: Optional[str] = None,
    non_interactive: bool = True,
    client: Optional[ServiceFoundryServiceClient] = None,
) -> Workspace:
    client = client or ServiceFoundryServiceClient.get_client()
    if non_interactive:
        if not name_or_id:
            raise ValueError("workspace name or id cannot be null")

    cluster = resolve_cluster_or_error(
        name_or_id=cluster_name_or_id,
        ignore_context=False,
        non_interactive=non_interactive,
        client=client,
    )

    workspace, cluster = resolve_workspace_or_error(
        name_or_id=name_or_id,
        cluster_name_or_id=cluster,
        ignore_context=True,
        non_interactive=non_interactive,
        client=client,
    )
    client.session.set_workspace(workspace.to_dict_for_session())
    console.print(PROMPT_SETTING_WORKSPACE_CONTEXT.format(workspace.name))
    client.session.set_cluster(cluster.to_dict_for_session())
    console.print(PROMPT_SETTING_CLUSTER_CONTEXT.format(cluster.name))
    client.session.save_session()
    return workspace


def clear_context(
    non_interactive: bool = True,
    client: Optional[ServiceFoundryServiceClient] = None,
):
    client = client or ServiceFoundryServiceClient.get_client()
    client.session.set_cluster(None)
    client.session.set_workspace(None)
    client.session.save_session()
