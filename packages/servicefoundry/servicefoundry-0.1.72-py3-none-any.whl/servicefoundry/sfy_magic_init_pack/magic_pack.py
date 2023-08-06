from pathlib import Path
from platform import python_version
from typing import Dict, Optional

from pydantic import BaseModel

from servicefoundry.io.input_hook import InputHook
from servicefoundry.io.output_callback import OutputCallBack
from servicefoundry.lib.exceptions import ConfigurationException
from servicefoundry.service_definition.definition import (
    CPU,
    Memory,
    ServiceFoundryBuildDefinition,
    ServiceFoundryDefinition,
)
from servicefoundry.sfy_init.pack import Pack


class Parameters(BaseModel):
    name: str
    workspace: str
    cpu: Optional[CPU]
    memory: Optional[Memory]


class MagicPack(Pack):
    def __init__(
        self,
        python_file: str,
        additional_requirements: Dict[str, str],
        parameters: Parameters,
    ):
        self.python_file = python_file
        if not Path(python_file).exists():
            raise ConfigurationException(f"Couldn't find file {self.python_file}.")
        self.additional_requirements = additional_requirements
        self.parameters = parameters

    def get_default_service_name(self):
        return "should-be-changed"

    def get_description(self):
        return None

    def ask_questions(self, input_hook: InputHook, output_hook: OutputCallBack):
        pass

    def get_default_definition(self) -> ServiceFoundryDefinition:
        definition = super().get_default_definition()
        definition.service.name = self.parameters.name
        definition.service.workspace = self.parameters.workspace
        # TODO @cloud All this validation shouldn't happen here
        if self.parameters.cpu:
            if not self.parameters.cpu.limit:
                self.parameters.cpu.limit = self.parameters.cpu.required
            elif self.parameters.cpu.limit < self.parameters.cpu.required:
                raise ConfigurationException(f"CPU limit can't be less than required.")
            definition.service.cpu = self.parameters.cpu
        if self.parameters.memory:
            if not self.parameters.memory.limit:
                self.parameters.memory.limit = self.parameters.memory.required
            elif self.parameters.memory.limit < self.parameters.memory.required:
                raise ConfigurationException(
                    f"Memory limit can't be less than required."
                )
            definition.service.memory = self.parameters.memory
        definition.build = ServiceFoundryBuildDefinition(
            build_pack="sfy_build_pack_python",
            options={"python_version": f"python:{python_version()}"},
        )
        return definition
