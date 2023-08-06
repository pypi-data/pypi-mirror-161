import os
from typing import Optional

from servicefoundry.lib.clients.auth_service_client import AuthServiceClient
from servicefoundry.lib.config_utils import (
    _get_profile,
    _get_session,
    _migrate_old_session_to_new_config,
    _save_session,
)
from servicefoundry.lib.const import API_KEY_ENV_NAMES, DEFAULT_PROFILE_NAME
from servicefoundry.lib.exceptions import BadRequestException
from servicefoundry.lib.model.session import ServiceFoundrySession


def _get_api_key_from_env() -> Optional[str]:
    for key_name in API_KEY_ENV_NAMES:
        value = os.getenv(key_name)
        if value:
            return value


def get_session(profile_name: str = DEFAULT_PROFILE_NAME):
    _migrate_old_session_to_new_config()
    profile = _get_profile(name=profile_name)
    api_key = _get_api_key_from_env()
    if api_key:
        auth_client = AuthServiceClient(profile=profile)
        return auth_client.login_with_api_token(api_key=api_key)

    auth_client = AuthServiceClient(profile=profile)
    session = ServiceFoundrySession.from_profile(
        profile=profile, refresher=auth_client.refresh_token
    )
    if session:
        return session
    else:
        raise BadRequestException(403, f"Please login before running this command.")


def logout_session(profile_name: str = DEFAULT_PROFILE_NAME):
    # TODO: Implement logout if using api key
    _session_dict = _get_session(profile_name=profile_name)
    if _session_dict:
        _save_session(session={}, profile_name=profile_name)
    else:
        raise BadRequestException(403, f"Please login before running this command.")
