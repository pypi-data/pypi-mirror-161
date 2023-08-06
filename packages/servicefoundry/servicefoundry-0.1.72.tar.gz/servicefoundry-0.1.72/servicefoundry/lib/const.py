import os
from pathlib import Path

DEFAULT_BASE_URL = "https://app.truefoundry.com"
API_SERVER_RELATIVE_PATH = "api/svc"
DEFAULT_API_SERVER = f"{DEFAULT_BASE_URL.rstrip('/')}/{API_SERVER_RELATIVE_PATH}"
DEFAULT_AUTH_UI = DEFAULT_BASE_URL
DEFAULT_AUTH_SERVER = (
    "https://auth-server.tfy-ctl-euwe1-production.production.truefoundry.com"
)
DEFAULT_TENANT_NAME = "truefoundry"
DEFAULT_PROFILE_NAME = "default"
API_KEY_ENV_NAMES = [
    "SERVICEFOUNDRY_API_KEY",
    "SFY_API_KEY",
    "TRUEFOUNDRY_API_KEY",
    "SERVICE_FOUNDRY_API_KEY",
]

_SFY_CONFIG_DIR = Path.home() / ".truefoundry"
SFY_CONFIG_DIR = str(_SFY_CONFIG_DIR)  # as a directory
SFY_PROFILES_FILEPATH = str(_SFY_CONFIG_DIR / "profiles.json")  # as a directory
SFY_SESSIONS_FILEPATH = str(_SFY_CONFIG_DIR / "sessions.json")  # as a directory
OLD_SESSION_FILEPATH = str(
    Path.home() / ".truefoundry"
)  # as a filepath, to be removed in future versions

# Build related Config
SERVICE_DEF_FILE_NAME = "servicefoundry.yaml"
TEMPLATE_DEF_FILE_NAME = "template.yaml"
SFY_DIR = ".servicefoundry"
BUILD_DIR = os.path.join(SFY_DIR, "build")

COMPONENT = "Component"
BUILD_PACK = "BuildPack"
KIND = "kind"

# Polling during login redirect
MAX_POLLING_RETRY = 100
POLLING_SLEEP_TIME_IN_SEC = 4

# Refresh access token cutoff
REFRESH_ACCESS_TOKEN_IN_SEC = 10 * 60

ENTITY_JSON_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
