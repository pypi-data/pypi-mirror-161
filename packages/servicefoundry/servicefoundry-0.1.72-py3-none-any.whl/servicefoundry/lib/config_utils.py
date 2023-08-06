import json
import os
from typing import Any, Dict

from servicefoundry.internal.util import json_default_encoder
from servicefoundry.lib.const import (
    DEFAULT_PROFILE_NAME,
    OLD_SESSION_FILEPATH,
    SFY_CONFIG_DIR,
    SFY_PROFILES_FILEPATH,
    SFY_SESSIONS_FILEPATH,
)
from servicefoundry.lib.model.entity import Profile


def _ensure_config_dir():
    os.makedirs(SFY_CONFIG_DIR, exist_ok=True)


def _save_profiles(profiles: Dict[str, Profile]):
    with open(SFY_PROFILES_FILEPATH, "w") as f:
        json.dump(
            {name: profile.to_dict() for name, profile in profiles.items()},
            f,
            default=json_default_encoder,
        )


def _create_profiles_file() -> Dict[str, Profile]:
    profiles = {DEFAULT_PROFILE_NAME: Profile()}
    _save_profiles(profiles)
    return profiles


def _save_sessions(sessions: Dict[str, Dict[str, Any]]):
    with open(SFY_SESSIONS_FILEPATH, "w") as f:
        json.dump(
            sessions,
            f,
            default=json_default_encoder,
        )


def _create_sessions_file():
    sessions = {DEFAULT_PROFILE_NAME: {}}
    _save_sessions(sessions)
    return sessions


def _migrate_old_session_to_new_config():
    # To be removed in future version
    if os.path.exists(OLD_SESSION_FILEPATH) and os.path.isfile(OLD_SESSION_FILEPATH):
        with open(OLD_SESSION_FILEPATH) as f:
            session_data = json.load(f)
        os.remove(OLD_SESSION_FILEPATH)
        _ensure_config_dir()
        # TODO: this saving is not ideal as there is no validation!
        sessions = {DEFAULT_PROFILE_NAME: session_data}
        _save_sessions(sessions)


def _get_profiles() -> Dict[str, Profile]:
    with open(SFY_PROFILES_FILEPATH) as f:
        profiles = json.load(f)
        profiles = {key: Profile.from_dict(value) for key, value in profiles.items()}
    return profiles


def _get_or_create_profiles() -> Dict[str, Profile]:
    _migrate_old_session_to_new_config()
    _ensure_config_dir()
    if not os.path.exists(SFY_PROFILES_FILEPATH):
        profiles = _create_profiles_file()
    else:
        profiles = _get_profiles()

    if not profiles or not profiles.get(DEFAULT_PROFILE_NAME):
        profiles = _create_profiles_file()

    return profiles


def _save_profile(profile: Profile):
    profiles = _get_or_create_profiles()
    profiles[profile.name] = profile
    _save_profiles(profiles)


def _get_profile(name: str = DEFAULT_PROFILE_NAME) -> Profile:
    profiles = _get_or_create_profiles()
    return profiles[name]


def _get_sessions() -> Dict[str, Dict[str, Any]]:
    with open(SFY_SESSIONS_FILEPATH) as f:
        sessions = json.load(f)
    return sessions


def _get_or_create_sessions() -> Dict[str, Dict[str, Any]]:
    _migrate_old_session_to_new_config()
    _ensure_config_dir()
    if not os.path.exists(SFY_SESSIONS_FILEPATH):
        sessions = _create_sessions_file()
    else:
        sessions = _get_sessions()

    if not sessions:
        sessions = _create_sessions_file()

    return sessions


def _save_session(session: Dict[str, Any], profile_name: str):
    sessions = _get_or_create_sessions()
    sessions[profile_name] = session
    _save_sessions(sessions)


def _get_session(profile_name: str) -> Dict[str, Any]:
    sessions = _get_or_create_sessions()
    return sessions[profile_name]
