from pathlib import Path
from typing import Optional, Sequence, Union

from servicefoundry.lib.clients.service_foundry_client import (
    ServiceFoundryServiceClient,
)
from servicefoundry.lib.const import SERVICE_DEF_FILE_NAME
from servicefoundry.lib.exceptions import ConfigurationException
from servicefoundry.service_definition.definition import ServiceFoundryDefinition
from servicefoundry.sfy_build.const import BUILD_DIR
from servicefoundry.utils.file_utils import make_tarfile


# TODO: Move this to internal, this is not part of public API
def deploy(
    directory: Path,
    additional_directories: Sequence[Union[Path, str]] = None,
    tfs_client: Optional[ServiceFoundryServiceClient] = None,
    workspace: Optional[str] = None,  # fqn
    **kwargs,
):
    additional_directories = additional_directories or []
    tfs_client = tfs_client or ServiceFoundryServiceClient.get_client()
    definition_file = directory / SERVICE_DEF_FILE_NAME
    if not definition_file.is_file():
        raise ConfigurationException(f"Couldn't find {definition_file}.")
    sfy_yaml = ServiceFoundryDefinition.from_yaml(definition_file)
    service_def = sfy_yaml.to_service_def(workspace=workspace)
    build_dir = Path(BUILD_DIR)
    build_dir.mkdir(parents=True, exist_ok=True)
    package_zip = build_dir / "build.tar.gz"
    make_tarfile(
        package_zip, directory, additional_directories, ignore_list=[BUILD_DIR]
    )
    deployment = tfs_client.build_and_deploy(service_def, package_zip)
    return deployment
