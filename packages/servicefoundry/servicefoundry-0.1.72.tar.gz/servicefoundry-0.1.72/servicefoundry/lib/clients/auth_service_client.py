import logging
import time

import requests

from servicefoundry.internal.util import request_handling
from servicefoundry.lib.const import MAX_POLLING_RETRY, POLLING_SLEEP_TIME_IN_SEC
from servicefoundry.lib.model.entity import Profile
from servicefoundry.lib.model.session import ServiceFoundrySession

logger = logging.getLogger(__name__)


class AuthServiceClient:
    def __init__(self, profile: Profile):
        self.profile = profile
        self.host = self.profile.server_config.auth_server

    def refresh_token(self, session: ServiceFoundrySession):
        url = f"{self.host}/api/v1/oauth/token/refresh"
        data = {
            "tenantName": session.profile.server_config.tenant_name,
            "refreshToken": session.refresh_token,
        }
        res = requests.post(url, data=data)
        res = request_handling(res)
        return res["accessToken"], res["refreshToken"]

    def get_device_code(self):
        url = f"{self.host}/api/v1/oauth/device"
        data = {"tenantName": self.profile.server_config.tenant_name}
        res = requests.post(url, data=data)
        res = request_handling(res)
        return (
            f"{self.profile.server_config.auth_ui}/authorize/device?userCode={res['userCode']}",
            res["userCode"],
            res["deviceCode"],
        )

    def poll_for_auth(self, device_code):
        i = 0
        while i < MAX_POLLING_RETRY:
            try:
                return self._poll_for_auth(device_code)
            except RetryError:
                time.sleep(POLLING_SLEEP_TIME_IN_SEC)
                i = i + 1

    def _poll_for_auth(self, device_code):
        url = f"{self.host}/api/v1/oauth/device/token"
        data = {
            "tenantName": self.profile.server_config.tenant_name,
            "deviceCode": device_code,
        }
        res = requests.post(url, data=data)
        res = request_handling(res)
        if "message" in res and res["message"] == "authorization_pending":
            raise RetryError()
        return ServiceFoundrySession(
            profile=self.profile,
            access_token=res["accessToken"],
            refresh_token=res["refreshToken"],
            refresher=self.refresh_token,
        )

    def login_with_api_token(self, api_key: str):
        url = f"{self.host}/api/v1/oauth/api-keys/token"
        data = {"apiKey": api_key}
        res = requests.post(url, data=data)
        res = request_handling(res)
        return ServiceFoundrySession(
            profile=self.profile,
            access_token=res["accessToken"],
            refresh_token=res["refreshToken"],
            refresher=self.refresh_token,
        )


class RetryError(Exception):
    def __init__(self):
        super()
