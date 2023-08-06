import time
from typing import Any, Callable, Dict, Optional, Tuple

import jwt

from servicefoundry.lib.config_utils import _get_session, _save_session
from servicefoundry.lib.model.entity import Profile


# TODO: convert to Pydantic if possible for easy recursive serde
class ServiceFoundrySession:
    def __init__(
        self,
        profile: Profile,
        access_token: str,
        refresh_token: str,
        refresher: Callable[["ServiceFoundrySession"], Tuple[str, str]],
        cluster=None,
        workspace=None,
        **kwargs,
    ):
        self.profile = profile
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.refresher = refresher
        self.cluster = cluster
        self.workspace = workspace

    @classmethod
    def from_profile(
        cls,
        profile: Profile,
        refresher: Callable[["ServiceFoundrySession"], Tuple[str, str]],
    ) -> Optional["ServiceFoundrySession"]:
        # TODO (chiragjn): because we are not using pydantic, the datetimes in cluster and workspace
        #                  are not parsed at all! This is not a new bug but needs to be fixed for correctness
        session_dict = _get_session(profile_name=profile.name)
        try:
            return cls(profile=profile, refresher=refresher, **session_dict)
        except TypeError:
            return None

    def save_session(self):
        session_dict = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "cluster": self.cluster,
            "workspace": self.workspace,
        }
        _save_session(session_dict, profile_name=self.profile.name)

    def refresh_access_token(self):
        self.access_token, self.refresh_token = self.refresher(self)
        self.save_session()

    def get_expiry(self):
        return self.decode()["exp"]

    def get_ttl(self):
        return self.get_expiry() - time.time()

    def get_user_details(self):
        decoded = self.decode()
        return {"username": decoded["preferred_username"], "email": decoded["email"]}

    def decode(self):
        return jwt.decode(self.access_token, options={"verify_signature": False})

    def set_cluster(self, cluster: Optional[Dict[str, Any]]):
        self.cluster = cluster
        return cluster

    def get_cluster(self) -> Optional[Dict[str, Any]]:
        return self.cluster

    def set_workspace(self, workspace: Optional[Dict[str, Any]]):
        self.workspace = workspace
        return workspace

    def get_workspace(self) -> Optional[Dict[str, Any]]:
        return self.workspace
