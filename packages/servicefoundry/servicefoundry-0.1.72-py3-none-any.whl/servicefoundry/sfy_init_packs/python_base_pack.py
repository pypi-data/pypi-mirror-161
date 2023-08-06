from platform import python_version

from servicefoundry.io.input_hook import InputHook
from servicefoundry.io.output_callback import OutputCallBack
from servicefoundry.io.parameters import OptionsParameter
from servicefoundry.service_definition.definition import (
    ServiceFoundryBuildDefinition,
    ServiceFoundryDefinition,
)
from servicefoundry.sfy_build_pack_python.docker_file import (
    PYTHON_37,
    PYTHON_38,
    PYTHON_39,
    PYTHON_310,
)
from servicefoundry.sfy_init.pack import Pack


class PythonBasePack(Pack):

    python_version = None

    def ask_questions(self, input_hook: InputHook, output_hook: OutputCallBack):
        python_current = f"python:{python_version()}"
        param = OptionsParameter(
            prompt="Choose a Python version?",
            options={
                python_current: f"current - {python_current}",
                PYTHON_37: PYTHON_37,
                PYTHON_38: PYTHON_38,
                PYTHON_39: PYTHON_39,
                PYTHON_310: PYTHON_310,
            },
        )
        self.python_version = input_hook.ask_option(param)

    def get_default_definition(self) -> ServiceFoundryDefinition:
        definition = super().get_default_definition()
        definition.build = ServiceFoundryBuildDefinition(
            build_pack="sfy_build_pack_python",
            options={"python_version": self.python_version},
        )
        return definition
