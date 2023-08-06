from pathlib import Path

from servicefoundry.core.notebook.notebook_util import get_default_callback
from servicefoundry.io.input_hook import FailInputHook
from servicefoundry.lib.clients.service_foundry_client import (
    ServiceFoundryServiceClient,
)
from servicefoundry.sfy_deploy.deploy import deploy
from servicefoundry.sfy_init.init_flow import InitTemplateFlow
from servicefoundry.sfy_magic_init_pack.auto_service_magic_pack import (
    AutoServiceMagicPack,
)
from servicefoundry.sfy_magic_init_pack.auto_webapp_magic_pack import (
    AutoWebappMagicPack,
)
from servicefoundry.sfy_magic_init_pack.gradio_magic_pack import GradioMagicPack
from servicefoundry.sfy_magic_init_pack.magic_pack import MagicPack, Parameters


class Component:
    def __init__(self, pack: MagicPack):
        self.pack = pack

    def deploy(self, working_dir="./"):
        # TODO (chiragjn): Add support to override parts of the definition here e.g. deploying to a different workspace
        base_dir = Path(".servicefoundry")
        init_flow = InitTemplateFlow(
            self.pack,
            input_hook=FailInputHook(),
            output_hook=get_default_callback(),
            base_directory=base_dir,
            is_cli=False,
        )
        package_dir = init_flow.create_project()
        tfs_client = ServiceFoundryServiceClient.get_client()
        deploy(
            directory=package_dir,
            additional_directories=[working_dir],
            client=tfs_client,
        )


class Service(Component):
    def __init__(self, python_file: str, requirements: dict, parameters: Parameters):
        pack = AutoServiceMagicPack(python_file, requirements, parameters)
        super().__init__(pack)


class Webapp(Component):
    def __init__(self, python_file: str, requirements: dict, parameters: Parameters):
        pack = AutoWebappMagicPack(python_file, requirements, parameters)
        super().__init__(pack)


class Gradio(Component):
    def __init__(self, python_file: str, requirements: dict, parameters: Parameters):
        pack = GradioMagicPack(python_file, requirements, parameters)
        super().__init__(pack)
